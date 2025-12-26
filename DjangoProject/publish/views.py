import os
import uuid
import json
import re
from django.conf import settings
from django.http import JsonResponse, FileResponse, Http404, HttpResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from api.models import Post, Tag
from api.serializers import PostSerializer
from .serializers import CreatePostSerializer, CreateTagSerializer, CurrentUserSerializer

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def create_post(request):
    """发布动态接口，GET 返回当前用户自己的帖子列表"""
    if request.method == 'GET':
        posts = Post.objects.filter(user=request.user).order_by('-created_at')
        # 清理历史数据中的伪 poster，防止 404，并去重 media
        cleaned = []
        def dedupe(seq):
            seen = set()
            out = []
            for x in seq:
                if x and x not in seen:
                    seen.add(x)
                    out.append(x)
            return out
        for p in posts:
            if p.type == 'video':
                media = dedupe(p.media or [])
                image_regex = re.compile(r'\.(png|jpe?g|webp|gif)$', re.IGNORECASE)
                video_url = ''
                images = []
                for m in media:
                    if not m:
                        continue
                    if not video_url and not image_regex.search(m):
                        # 第一个非空、非图片认为是视频
                        video_url = m
                    elif image_regex.search(m):
                        # 跳过存放在 /uploads/videos/ 下的伪封面，避免 404
                        if '/uploads/videos/' in m:
                            continue
                        images.append(m)
                # 返回视频 + 附带的图片（不含 poster 字段，因为 poster 已单独返回）
                if video_url:
                    p.media = [video_url] + images
                else:
                    # 实际没有视频，退化为图片列表
                    p.media = images
            else:
                # 图片或其他类型去重并移除空值
                p.media = dedupe(p.media or [])
            cleaned.append(p)
        serializer = PostSerializer(cleaned, many=True, context={'request': request})
        return Response(serializer.data)

    serializer = CreatePostSerializer(data=request.data)
    
    if serializer.is_valid():
        validated_data = serializer.validated_data
        user = request.user
        visibility = validated_data.get('visibility', 'public')
        
        # 确定动态类型
        post_type = 'text'
        media = []
        
        # 处理图片
        images = validated_data.get('images', [])
        if images:
            post_type = 'image'
            media.extend(images)
        
        # 处理视频
        video = validated_data.get('video', '')
        video_poster = validated_data.get('videoPoster', '')
        if video:
            post_type = 'video'
            media.append(video)
            # 只有实际存在的封面才附加
            if video_poster:
                media.append(video_poster)
        
        # 创建动态
        post = Post.objects.create(
            user=user,
            text=validated_data.get('text', ''),
            type=post_type,
            media=media,
            visibility=visibility
        )
        
        # 处理标签
        tags = validated_data.get('tags', [])
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name.strip())
            post.tags.add(tag)
        
        # 序列化返回结果（统一使用 api.Post）
        post_serializer = PostSerializer(post, context={'request': request})

        return Response({
            'success': True,
            'message': '发布成功',
            'data': post_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': '发布失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)


def serve_video_file(request, filename):
    """开发环境下的视频文件 Range 支持，手动处理 206 Partial Content"""
    file_path = os.path.join(settings.MEDIA_ROOT, 'uploads', 'videos', filename)
    print(f"[serve_video_file] 尝试访问: {file_path}")
    
    if not os.path.exists(file_path):
        raise Http404("Video file not found.")
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    # 处理 Range 请求
    range_header = request.META.get('HTTP_RANGE', '')
    if range_header:
        # 解析 Range 头: "bytes=start-end"
        range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if range_match:
            start = int(range_match.group(1))
            end = range_match.group(2)
            end = int(end) if end else file_size - 1
            
            # 验证范围
            if start >= file_size or end >= file_size or start > end:
                return JsonResponse({'error': 'Invalid Range'}, status=416)
            
            # 读取指定范围的内容
            content_length = end - start + 1
            file = open(file_path, 'rb')
            file.seek(start)
            content = file.read(content_length)
            file.close()
            
            # 返回 206 Partial Content 响应
            response = HttpResponse(content, status=206, content_type='video/mp4')
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Content-Length'] = str(content_length)
            response['Accept-Ranges'] = 'bytes'
            print(f"[serve_video_file] 返回 206 Partial Content: {start}-{end}/{file_size}")
            return response
    
    # 没有 Range 请求或格式错误，返回整个文件
    response = FileResponse(open(file_path, 'rb'), content_type='video/mp4')
    response['Content-Length'] = str(file_size)
    response['Accept-Ranges'] = 'bytes'
    print(f"[serve_video_file] 返回 200 OK，文件大小: {file_size}")
    return response

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    """图片上传接口"""
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'message': '请提供图片文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.name)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    
    # 保存文件并构建绝对 URL
    file_content = ContentFile(file.read())
    default_storage.save(os.path.join('uploads', 'images', filename), file_content)
    file_url = request.build_absolute_uri(f"/media/uploads/images/{filename}")
    
    return Response({
        'success': True,
        'data': {
            'url': file_url
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_video(request):
    """视频上传接口"""
    if 'file' not in request.FILES:
        return Response({
            'success': False,
            'message': '请提供视频文件'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    file = request.FILES['file']
    
    # 生成唯一文件名
    file_extension = os.path.splitext(file.name)[1]
    filename = f"{uuid.uuid4()}{file_extension}"
    
    # 保存文件并构建绝对 URL
    file_content = ContentFile(file.read())
    default_storage.save(os.path.join('uploads', 'videos', filename), file_content)
    file_url = request.build_absolute_uri(f"/media/uploads/videos/{filename}")
    
    # 视频封面URL：当前未生成实际封面，返回空字符串避免404
    video_poster_url = ''
    
    return Response({
        'success': True,
        'data': {
            'url': file_url,
            'poster': video_poster_url
        }
    }, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_common_tags(request):
    """获取常用标签接口"""
    # 定义一些常用标签
    common_tags = ['户外', '日常', '美食', '旅行', '运动', '摄影', '读书', '音乐', '电影', '宠物', '工作', '学习']
    
    # 确保这些标签存在于数据库中
    for tag_name in common_tags:
        Tag.objects.get_or_create(name=tag_name)
    
    return Response({
        'success': True,
        'data': {
            'tags': common_tags
        }
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_tag(request):
    """创建新标签接口"""
    serializer = CreateTagSerializer(data=request.data)
    
    if serializer.is_valid():
        tag, created = Tag.objects.get_or_create(name=serializer.validated_data['name'])
        
        if not created:
            return Response({
                'success': False,
                'message': '标签已存在'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': True,
            'message': '标签创建成功',
            'data': {
                'id': tag.id,
                'name': tag.name
            }
        }, status=status.HTTP_201_CREATED)
    
    return Response({
        'success': False,
        'message': '标签创建失败',
        'errors': serializer.errors
    }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前用户信息接口"""
    serializer = CurrentUserSerializer(request.user)
    return Response({
        'success': True,
        'data': serializer.data
    })
