from rest_framework import viewsets, status, pagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from .serializers import (
    UserSerializer, UserCreateSerializer,
    PostSerializer, CommentSerializer, CreateCommentSerializer,
    FriendshipSerializer
)
from .models import Post, Like, Comment, Friendship, Follow

# 简单的 staff 判断工具
def require_staff(user):
    return user and user.is_authenticated and user.is_staff


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # 默认允许匿名访问
    
    def get_permissions(self):
        """根据动作设置不同的权限"""
        if self.action in ['list', 'retrieve', 'create', 'update', 'partial_update', 'destroy', 'me']:
            return [IsAuthenticated()]  # 列表、详情、创建、更新、删除和获取当前用户信息需要认证
        return [AllowAny()]  # register 允许匿名访问
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer
    
    def create(self, request, *args, **kwargs):
        """重写创建方法，使用注册逻辑"""
        return self.register(request)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """获取当前用户信息"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post', 'get'], permission_classes=[AllowAny])
    def register(self, request):
        """用户注册"""
        if request.method == 'GET':
            return Response({
                'message': 'This is the user registration endpoint.',
                'method': 'POST',
                'required_fields': ['username', 'password'],
                'optional_fields': ['email', 'first_name', 'last_name'],
                'example': {
                    'username': 'newuser',
                    'password': 'securepassword',
                    'email': 'user@example.com'
                }
            })
        
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'message': 'User created successfully',
                'user': UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """用户登录接口"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Please provide both username and password'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # 获取或创建 token
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login successful',
            'token': token.key,
            'user': UserSerializer(user).data
        })
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)


# ===================== 管理端接口（最小实现） =====================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_users(request):
    """管理员用户列表，支持 search"""
    if not require_staff(request.user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    search = request.query_params.get('search', '')
    qs = User.objects.all().order_by('-date_joined')
    if search:
        qs = qs.filter(Q(username__icontains=search) | Q(email__icontains=search))
    paginator = StandardResultsSetPagination()
    result = paginator.paginate_queryset(qs, request)
    data = UserSerializer(result, many=True).data
    return paginator.get_paginated_response(data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def admin_toggle_user(request, user_id):
    """管理员启用/禁用用户，传 is_active bool"""
    if not require_staff(request.user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    try:
        target = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)
    is_active = request.data.get('is_active')
    if is_active is None:
        return Response({'detail': 'Missing is_active'}, status=status.HTTP_400_BAD_REQUEST)
    target.is_active = bool(is_active)
    target.save(update_fields=['is_active'])
    return Response({'success': True, 'id': target.id, 'is_active': target.is_active})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_list_posts(request):
    """管理员帖子列表，支持 keyword"""
    if not require_staff(request.user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    keyword = request.query_params.get('keyword', '')
    qs = Post.objects.all().order_by('-created_at')
    if keyword:
        qs = qs.filter(
            Q(text__icontains=keyword) |
            Q(user__username__icontains=keyword) |
            Q(tags__icontains=keyword)
        )
    paginator = StandardResultsSetPagination()
    result = paginator.paginate_queryset(qs, request)
    data = PostSerializer(result, many=True).data
    return paginator.get_paginated_response(data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def admin_delete_post(request, post_id):
    """管理员删除帖子"""
    if not require_staff(request.user):
        return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return Response({'success': True})
    except Post.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """用户登出接口"""
    try:
        # 删除用户的 token
        Token.objects.filter(user=request.user).delete()
        return Response({
            'message': 'Logout successful'
        })
    except Token.DoesNotExist:
        return Response({
            'message': 'No active session found'
        }, status=status.HTTP_400_BAD_REQUEST)

# 自定义分页类
class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pageSize'
    max_page_size = 100

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, post_id):
    """点赞/取消点赞接口"""
    try:
        post = Post.objects.get(id=post_id)
        liked = request.data.get('liked', True)
        
        if liked:
            # 点赞
            like, created = Like.objects.get_or_create(user=request.user, post=post)
            if not created:
                # 已经点赞过
                return Response({
                    'success': False,
                    'message': '已经点赞过'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            # 取消点赞
            try:
                like = Like.objects.get(user=request.user, post=post)
                like.delete()
            except Like.DoesNotExist:
                return Response({
                    'success': False,
                    'message': '未点赞过该动态'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新点赞数
        post.refresh_from_db()
        
        return Response({
            'success': True,
            'message': '操作成功',
            'data': {
                'likes': post.likes_count
            }
        })
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def post_comments(request, post_id):
    """获取动态评论列表和发布评论接口"""
    try:
        post = Post.objects.get(id=post_id)
        
        if request.method == 'GET':
            # 获取评论列表
            page = request.query_params.get('page', 1)
            page_size = request.query_params.get('pageSize', 10)
            
            # 按时间倒序获取评论
            comments = Comment.objects.filter(post=post).order_by('-created_at')
            
            # 分页
            paginator = StandardResultsSetPagination()
            paginator.page_size = page_size
            result_page = paginator.paginate_queryset(comments, request)
            
            # 序列化
            serializer = CommentSerializer(result_page, many=True, context={'request': request})
            
            return paginator.get_paginated_response({
                'success': True,
                'data': {
                    'comments': serializer.data,
                    'total': comments.count()
                }
            })
        elif request.method == 'POST':
            # 发布评论
            serializer = CreateCommentSerializer(data=request.data)
            
            if serializer.is_valid():
                comment = serializer.save(user=request.user, post=post)
                
                # 序列化返回的评论
                comment_serializer = CommentSerializer(comment, context={'request': request})
                
                return Response({
                    'success': True,
                    'message': '评论成功',
                    'data': comment_serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': '评论失败',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_post(request, post_id):
    """删除动态接口"""
    try:
        post = Post.objects.get(id=post_id)
        
        # 检查是否是动态的作者
        if post.user != request.user:
            return Response({
                'success': False,
                'message': '只能删除自己的动态'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # 删除相关的点赞和评论
        Like.objects.filter(post=post).delete()
        Comment.objects.filter(post=post).delete()
        
        # 删除动态
        post.delete()
        
        return Response({
            'success': True,
            'message': '删除成功'
        })
    except Post.DoesNotExist:
        return Response({
            'success': False,
            'message': '动态不存在'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_friend_request(request):
    """发起好友申请"""
    to_user_id = request.data.get('to_user_id')
    if not to_user_id:
        return Response({'success': False, 'message': '缺少 to_user_id'}, status=status.HTTP_400_BAD_REQUEST)
    if int(to_user_id) == request.user.id:
        return Response({'success': False, 'message': '不能添加自己为好友'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = User.objects.get(id=to_user_id)
    except User.DoesNotExist:
        return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

    fr, created = Friendship.objects.get_or_create(from_user=request.user, to_user=to_user)
    if not created and fr.status == 'accepted':
        return Response({'success': False, 'message': '已是好友'}, status=status.HTTP_400_BAD_REQUEST)
    fr.status = 'pending'
    fr.save()
    return Response({'success': True, 'message': '已发送好友申请', 'data': FriendshipSerializer(fr).data}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def respond_friend_request(request, pk):
    """接受或拒绝好友申请"""
    action = request.data.get('action')
    if action not in ['accept', 'reject']:
        return Response({'success': False, 'message': 'action 需为 accept/reject'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        fr = Friendship.objects.get(id=pk, to_user=request.user)
    except Friendship.DoesNotExist:
        return Response({'success': False, 'message': '申请不存在'}, status=status.HTTP_404_NOT_FOUND)

    if action == 'accept':
        fr.status = 'accepted'
        fr.save()
        return Response({'success': True, 'message': '已同意', 'data': FriendshipSerializer(fr).data})
    fr.status = 'rejected'
    fr.save()
    return Response({'success': True, 'message': '已拒绝', 'data': FriendshipSerializer(fr).data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friend_requests(request):
    """我收到的好友申请（待确认）"""
    qs = Friendship.objects.filter(to_user=request.user, status='pending').order_by('-created_at')
    data = FriendshipSerializer(qs, many=True).data
    return Response({'success': True, 'data': {'requests': data, 'total': qs.count()}})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_friends(request):
    """我的好友列表（已同意）"""
    qs = Friendship.objects.filter(
        status='accepted'
    ).filter(
        Q(from_user=request.user) | Q(to_user=request.user)
    )
    friends = []
    for fr in qs:
        friend = fr.to_user if fr.from_user_id == request.user.id else fr.from_user
        profile = getattr(friend, 'profile', None)
        friends.append({
            'id': friend.id,
            'username': friend.username,
            'friendship_id': fr.id,
            'avatar': profile.avatar if profile and profile.avatar else '',
            'signature': profile.signature if profile else ''
        })
    return Response({'success': True, 'data': {'friends': friends, 'total': len(friends)}})


# 关注/取关
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def follow_user(request, pk):
    """关注某人"""
    if request.user.id == pk:
        return Response({'success': False, 'message': '不能关注自己'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        target = User.objects.get(id=pk)
    except User.DoesNotExist:
        return Response({'success': False, 'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
    follow, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if not created:
        return Response({'success': False, 'message': '已关注'}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'success': True, 'message': '关注成功'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unfollow_user(request, pk):
    """取关"""
    deleted, _ = Follow.objects.filter(follower=request.user, following_id=pk).delete()
    if deleted:
        return Response({'success': True, 'message': '已取消关注'})
    return Response({'success': False, 'message': '未关注该用户'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_following(request):
    qs = Follow.objects.filter(follower=request.user).select_related('following')
    data = [{'id': f.following.id, 'username': f.following.username, 'avatar': getattr(f.following.profile, 'avatar', '')} for f in qs]
    return Response({'success': True, 'data': {'following': data, 'total': len(data)}})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_followers(request):
    qs = Follow.objects.filter(following=request.user).select_related('follower')
    data = [{'id': f.follower.id, 'username': f.follower.username, 'avatar': getattr(f.follower.profile, 'avatar', '')} for f in qs]
    return Response({'success': True, 'data': {'followers': data, 'total': len(data)}})
