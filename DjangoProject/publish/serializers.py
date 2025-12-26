from rest_framework import serializers
from django.contrib.auth.models import User
from api.models import Post, Tag
from api.serializers import PostSerializer

class CreatePostSerializer(serializers.ModelSerializer):
    """发布动态序列化器"""
    content = serializers.CharField(source='text', required=False)
    images = serializers.ListField(required=False, default=[])
    video = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    videoPoster = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='')
    tags = serializers.ListField(child=serializers.CharField(), required=False, default=[])
    visibility = serializers.ChoiceField(choices=['public', 'friends', 'private'], required=False, default='public')
    
    class Meta:
        model = Post
        fields = ['content', 'images', 'video', 'videoPoster', 'tags', 'visibility']
    
    def validate(self, data):
        """验证输入数据"""
        images = data.get('images', [])
        video = data.get('video', '')
        
        if not images and not video and not data.get('text', ''):
            raise serializers.ValidationError("至少需要提供文字、图片或视频中的一种")
        
        return data

class CreateTagSerializer(serializers.ModelSerializer):
    """创建标签序列化器"""
    class Meta:
        model = Tag
        fields = ['name']

class CurrentUserSerializer(serializers.ModelSerializer):
    """当前用户信息序列化器"""
    avatar = serializers.CharField(source='profile.avatar', default='')
    nickname = serializers.CharField(source='username', default='')
    
    class Meta:
        model = User
        fields = ['avatar', 'nickname']