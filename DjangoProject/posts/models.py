from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class Post(models.Model):
    VISIBILITY_CHOICES = (
        ('public', '公开'),
        ('friends', '好友可见'),
        ('private', '仅自己可见'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    text = models.TextField()
    type = models.CharField(max_length=10, choices=[('image', '图片'), ('video', '视频')])
    media = models.JSONField(default=list)  # 存储媒体URL列表
    tag = models.CharField(max_length=20)
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    created_time = models.DateTimeField(auto_now_add=True)

    def get_time_display(self):
        """计算时间差并返回友好显示"""
        now = datetime.now()
        diff = now - self.created_time.replace(tzinfo=None)
        if diff.seconds < 60:
            return f"{diff.seconds}秒前"
        elif diff.seconds < 3600:
            return f"{diff.seconds//60}分钟前"
        elif diff.days < 1:
            return f"{diff.seconds//3600}小时前"
        else:
            return f"{diff.days}天前"

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments_list')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)

    def get_time_display(self):
        """同Post的时间显示逻辑"""
        now = datetime.now()
        diff = now - self.created_time.replace(tzinfo=None)
        if diff.seconds < 60:
            return "刚刚"
        elif diff.seconds < 3600:
            return f"{diff.seconds//60}分钟前"
        elif diff.days < 1:
            return f"{diff.seconds//3600}小时前"
        else:
            return f"{diff.days}天前"

class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_rel')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_liked = models.BooleanField(default=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')  # 确保一个用户只能对一个帖子点赞一次