"""
URL configuration for DjangoProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from publish.views import serve_video_file
from rest_framework_simplejwt.views import (
    TokenObtainPairView,  # 获取Token（登录）
    TokenRefreshView,     # 刷新Token
)

# 注意路由匹配从上到下，确保视频 Range 视图优先于 static
urlpatterns = [
    # 开发环境视频 Range 支持（必须置前）
    path('media/uploads/videos/<str:filename>', serve_video_file, name='serve-video-file'),

    path('admin/', admin.site.urls),  # Django后台管理地址
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # 登录接口
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # 刷新Token接口
    path('api/', include('api.urls')),
    path('api/setting/', include('setting.urls')),
    path('api/user/', include('my.urls')),  # 我的应用接口
    # 统一使用 api 应用的 posts 接口，避免 posts 应用重复表/路由
    path('api/publish/', include('publish.urls')),  # 发布应用接口
    path('api/notifications/', include('notifications.urls')),  # 通知应用接口
]

# Add media files URL configuration for development environment
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
