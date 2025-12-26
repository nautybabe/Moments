from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    login_view,
    logout_view,
    toggle_like,
    post_comments,
    delete_post,
    send_friend_request,
    respond_friend_request,
    list_friend_requests,
    list_friends,
    follow_user,
    unfollow_user,
    list_following,
    list_followers,
    # admin
    admin_list_users,
    admin_toggle_user,
    admin_list_posts,
    admin_delete_post,
)
from .utils import health_check, api_info
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('info/', api_info, name='api-info'),
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('', include(router.urls)),
  
    # 注册搜索模块
    path('', include('api.search.urls')),
  
    # 帖子相关接口（与发现页共享）
    path('posts/<int:post_id>/like/', toggle_like, name='toggle-like'),
    path('posts/<int:post_id>/comments/', post_comments, name='post-comments'),
    path('posts/<int:post_id>/delete/', delete_post, name='delete-post'),
    # 好友关系
    path('friends/request/', send_friend_request, name='send-friend-request'),
    path('friends/requests/', list_friend_requests, name='list-friend-requests'),
    path('friends/<int:pk>/respond/', respond_friend_request, name='respond-friend-request'),
    path('friends/', list_friends, name='list-friends'),
    # 关注关系
    path('follow/<int:pk>/', follow_user, name='follow-user'),
    path('unfollow/<int:pk>/', unfollow_user, name='unfollow-user'),
    path('following/', list_following, name='list-following'),
    path('followers/', list_followers, name='list-followers'),
    # 管理端接口（最小）
    path('admin/users/', admin_list_users, name='admin-list-users'),
    path('admin/users/<int:user_id>/toggle/', admin_toggle_user, name='admin-toggle-user'),
    path('admin/posts/', admin_list_posts, name='admin-list-posts'),
    path('admin/posts/<int:post_id>/delete/', admin_delete_post, name='admin-delete-post'),
]
