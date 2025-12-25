from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
import os

from api.serializers import UserSerializer, UserUpdateSerializer, PasswordChangeSerializer


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def me(request):
    """获取或更新当前用户信息"""
    if request.method == "GET":
        serializer = UserSerializer(request.user)
        data = serializer.data
        profile = data.get("profile") or {}
        avatar = profile.get("avatar")
        if avatar and not avatar.startswith("http"):
            profile["avatar"] = request.build_absolute_uri(avatar)
            data["profile"] = profile
        return Response(data)

    serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    data = UserSerializer(user).data
    profile = data.get("profile") or {}
    avatar = profile.get("avatar")
    if avatar and not avatar.startswith("http"):
        profile["avatar"] = request.build_absolute_uri(avatar)
        data["profile"] = profile
    return Response(data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_avatar(request):
    """上传头像并返回可访问URL"""
    file_obj = request.FILES.get("file")
    if not file_obj:
        return Response({"error": "未收到文件"}, status=status.HTTP_400_BAD_REQUEST)

    # 统一存储到 media/avatars/<user_id>/filename
    user_id = request.user.id
    avatars_dir = os.path.join("avatars", str(user_id))
    filename = default_storage.save(os.path.join(avatars_dir, file_obj.name), ContentFile(file_obj.read()))
    avatar_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

    # 保存到用户资料
    profile = getattr(request.user, "profile", None)
    if profile:
        profile.avatar = avatar_url
        profile.save()

    return Response({"avatar": avatar_url})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """修改密码"""
    serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Password updated successfully"})


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """登录（token）"""
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"error": "Please provide both username and password"}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"message": "Login successful", "token": token.key, "user": UserSerializer(user).data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """登出并清理 token"""
    Token.objects.filter(user=request.user).delete()
    return Response({"message": "Logout successful"})
