####################  搜索部分开始  ######################
from rest_framework import serializers
from django.contrib.auth import get_user_model
from api.models import Post
from .models import SearchHistory
from api.serializers import UserSerializer
from django.utils import timezone

User = get_user_model()

# --------------- 1.Post  ---------------
class PostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.SerializerMethodField(read_only=True)
    time = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)
    text = serializers.CharField(read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'user', 'avatar', 'text', 'type', 'media', 'visibility', 'created_at',
            'likes_count', 'comments_count', 'is_liked', 'time', 'tags'
        ]
        read_only_fields = [
            'id', 'user', 'avatar', 'text', 'likes_count', 'comments_count',
            'is_liked', 'time', 'tags', 'visibility', 'created_at'
        ]

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(user=user).exists()

    def get_time(self, obj):
        now = timezone.now()
        diff = now - obj.created_at
        if diff.days == 0:
            return obj.created_at.strftime("今天 %H:%M")
        elif diff.days == 1:
            return "昨天 " + obj.created_at.strftime("%H:%M")
        elif diff.days < 7:
            return f"{diff.days}天前"
        else:
            return obj.created_at.strftime("%m-%d %H:%M")

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_avatar(self, obj):
        profile = getattr(obj.user, 'profile', None)
        if profile and profile.avatar:
            return profile.avatar
        return ''

# --------------- 2.搜索历史  ---------------
class SearchHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchHistory
        fields = ['keyword','tag','date']
####################  搜索部分结束  ######################