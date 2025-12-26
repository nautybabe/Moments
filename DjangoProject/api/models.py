from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    """扩展用户资料"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    # 用 CharField 兼容 H5/小程序本地路径、网络 URL
    avatar = models.CharField(max_length=500, blank=True, default='')
    signature = models.CharField(max_length=120, blank=True, default='')

    def __str__(self):
        return f'Profile({self.user.username})'


class Post(models.Model):
    """动态模型"""
    VISIBILITY_CHOICES = (
        ('public', '公开'),
        ('friends', '好友可见'),
        ('private', '仅自己可见'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_posts')
    text = models.TextField(blank=True, default='')
    type = models.CharField(max_length=20, default='text')  # image, text, etc.
    media = models.JSONField(default=list)  # 存储媒体URL列表
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_at = models.DateTimeField(auto_now_add=True)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)

    def __str__(self):
        return f'Post({self.id}) by {self.user.username}'


class Like(models.Model):
    """点赞模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # 一个用户只能给一个动态点赞一次

    def __str__(self):
        return f'Like by {self.user.username} on Post({self.post.id})'


class Comment(models.Model):
    """评论模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on Post({self.post.id})'


class Tag(models.Model):
    """标签模型"""
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # 关联到Post的多对多关系
    posts = models.ManyToManyField(Post, related_name='tags', blank=True)

    def __str__(self):
        return self.name


class Friendship(models.Model):
    """好友关系（双向，同意后视为好友）"""
    STATUS_CHOICES = (
        ('pending', '待确认'),
        ('accepted', '已同意'),
        ('rejected', '已拒绝'),
    )
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_sent')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='friend_requests_received')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username} ({self.status})"


class Follow(models.Model):
    """关注关系（单向）；互相关注即好友"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_set')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers_set')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} -> {self.following.username}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()


@receiver(post_save, sender=Like)
def update_likes_count(sender, instance, created, **kwargs):
    """点赞后更新动态的点赞数"""
    if created:
        instance.post.likes_count += 1
        instance.post.save()


@receiver(post_save, sender=Comment)
def update_comments_count(sender, instance, created, **kwargs):
    """评论后更新动态的评论数"""
    if created:
        instance.post.comments_count += 1
        instance.post.save()


@receiver(models.signals.post_delete, sender=Like)
def update_likes_count_delete(sender, instance, **kwargs):
    """取消点赞后更新动态的点赞数"""
    instance.post.likes_count = max(0, instance.post.likes_count - 1)
    instance.post.save()


@receiver(models.signals.post_delete, sender=Comment)
def update_comments_count_delete(sender, instance, **kwargs):
    """删除评论后更新动态的评论数"""
    instance.post.comments_count = max(0, instance.post.comments_count - 1)
    instance.post.save()
