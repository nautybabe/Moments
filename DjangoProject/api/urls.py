from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, logout_view, toggle_like, post_comments, delete_post
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
]
