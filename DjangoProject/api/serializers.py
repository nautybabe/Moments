from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Profile, Post, Like, Comment, Tag, Friendship


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['avatar', 'signature']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined']

    def to_representation(self, instance):
        # 确保旧用户也有 profile 以避免序列化时报错
        Profile.objects.get_or_create(user=instance)
        return super().to_representation(instance)


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'profile']

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        user = super().update(instance, validated_data)
        if profile_data:
            profile, _ = Profile.objects.get_or_create(user=user)
            serializer = ProfileSerializer(profile, data=profile_data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return user


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("旧密码不正确")
        return value

    def validate_new_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("新密码至少6位")
        # 不做其他复杂校验，满足“位数以外不限制”
        return value

    def save(self, **kwargs):
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user


class CommentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.username', read_only=True)
    avatar = serializers.CharField(source='user.profile.avatar', read_only=True)
    time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'name', 'avatar', 'content', 'time']
        read_only_fields = ['id', 'name', 'avatar', 'time']

    def get_time(self, obj):
        """格式化时间为友好显示"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            # 今天
            return obj.created_at.strftime("今天 %H:%M")
        elif diff.days == 1:
            # 昨天
            return "昨天 " + obj.created_at.strftime("%H:%M")
        elif diff.days < 7:
            # 一周内
            return f"{diff.days}天前"
        else:
            # 超过一周
            return obj.created_at.strftime("%m-%d %H:%M")


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class FriendshipSerializer(serializers.ModelSerializer):
    from_user = serializers.PrimaryKeyRelatedField(read_only=True)
    to_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Friendship
        fields = ['id', 'from_user', 'to_user', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'from_user', 'status', 'created_at', 'updated_at']


class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    comment = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    visibility = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'user', 'text', 'type', 'media', 'visibility', 'created_at', 'likes_count', 'comments_count', 'comment', 'is_liked', 'time', 'tags']
        read_only_fields = ['id', 'user', 'likes_count', 'comments_count', 'comment', 'is_liked', 'time', 'tags', 'visibility']

    def get_comment(self, obj):
        """获取该动态的最新3条评论"""
        comments = obj.comments.all().order_by('-created_at')[:3]
        return CommentSerializer(comments, many=True).data

    def get_is_liked(self, obj):
        """检查当前用户是否已点赞该动态"""
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()
        return False

    def get_time(self, obj):
        """格式化时间为友好显示"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            # 今天
            return obj.created_at.strftime("今天 %H:%M")
        elif diff.days == 1:
            # 昨天
            return "昨天 " + obj.created_at.strftime("%H:%M")
        elif diff.days < 7:
            # 一周内
            return f"{diff.days}天前"
        else:
            # 超过一周
            return obj.created_at.strftime("%m-%d %H:%M")

    def get_tags(self, obj):
        """获取动态的标签列表"""
        return [tag.name for tag in obj.tags.all()]


class CreatePostSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    visibility = serializers.ChoiceField(choices=Post.VISIBILITY_CHOICES, default='public')

    class Meta:
        model = Post
        fields = ['text', 'type', 'media', 'visibility', 'tags']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        validated_data['user'] = self.context['request'].user
        post = Post.objects.create(**validated_data)
        # 处理标签：按名称获取或创建
        if tags_data:
            tag_objs = []
            for name in tags_data:
                name = name.strip()
                if not name:
                    continue
                tag_obj, _ = Tag.objects.get_or_create(name=name)
                tag_objs.append(tag_obj)
            if tag_objs:
                post.tags.set(tag_objs)
        return post
