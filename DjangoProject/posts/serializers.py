from rest_framework import serializers
from .models import Post, Comment, Like
from django.contrib.auth.models import User
from datetime import datetime

class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class PostSerializer(serializers.ModelSerializer):
    # 新增：匹配文档的liked字段（判断当前用户是否已点赞）
    liked = serializers.SerializerMethodField()
    # 可选：如果需要返回用户名和头像，补充以下字段（匹配文档响应）
    name = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    visibility = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        # 匹配文档的响应字段
        fields = ['id', 'name', 'avatar', 'time', 'text', 'type', 'media', 'tag', 'visibility', 'likes', 'comments', 'liked']

    # 获取当前用户是否已点赞
    def get_liked(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False  # 未登录返回false
        return Like.objects.filter(post=obj, user=request.user).exists()

    # 生成用户头像（优先用户设置的头像）
    def get_avatar(self, obj):
        profile = getattr(obj.user, 'profile', None)
        avatar = getattr(profile, 'avatar', '') if profile else ''
        if avatar:
            return avatar
        return f"https://picsum.photos/200?{obj.user.id}"

    # 时间格式化（匹配文档的“2分钟前”格式）
    def get_time(self, obj):
        now = datetime.now()
        diff = now - obj.created_time.replace(tzinfo=None)
        if diff.seconds < 60:
            return "刚刚"
        elif diff.seconds < 3600:
            return f"{diff.seconds//60}分钟前"
        elif diff.days < 1:
            return f"{diff.seconds//3600}小时前"
        else:
            return f"{diff.days}天前"

class CommentSerializer(serializers.ModelSerializer):
    # 关键修改：CharField → ReadOnlyField（避免required=True导致验证失败）
    name = serializers.ReadOnlyField(source='user.username')
    avatar = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'name', 'avatar', 'content', 'time']
        # 补充：明确所有只读字段（可选，但更规范）
        read_only_fields = ['id', 'name', 'avatar', 'time']

    def get_avatar(self, obj):
        return f"https://picsum.photos/200?{obj.user.id}"

    def get_time(self, obj):
        return obj.get_time_display()

class LikeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    message = serializers.CharField(default="操作成功")
    data = serializers.DictField(child=serializers.IntegerField(), default={'likes': 0})