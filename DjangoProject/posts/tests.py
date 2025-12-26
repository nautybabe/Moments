from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory, force_authenticate

from .models import Post
from api.models import Friendship


class PostVisibilityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.factory = APIRequestFactory()
        # 创建用户
        self.user0 = User.objects.create_user(username="user0", password="password0")
        self.user1 = User.objects.create_user(username="user1", password="password1")

        # user0 发帖：public/friends/private
        self.p0_public = Post.objects.create(
            user=self.user0, text="p0 public", type="image", media=[], tag="", visibility="public"
        )
        self.p0_friends = Post.objects.create(
            user=self.user0, text="p0 friends", type="image", media=[], tag="", visibility="friends"
        )
        self.p0_private = Post.objects.create(
            user=self.user0, text="p0 private", type="image", media=[], tag="", visibility="private"
        )

        # user1 发帖：public/friends/private
        self.p1_public = Post.objects.create(
            user=self.user1, text="p1 public", type="image", media=[], tag="", visibility="public"
        )
        self.p1_friends = Post.objects.create(
            user=self.user1, text="p1 friends", type="image", media=[], tag="", visibility="friends"
        )
        self.p1_private = Post.objects.create(
            user=self.user1, text="p1 private", type="image", media=[], tag="", visibility="private"
        )

    def _extract_ids(self, resp_json):
        return [item["id"] for item in resp_json["data"]["posts"]]

    def _call_list(self, user=None):
        from .views import PostListView

        request = self.factory.get("/posts/")
        if user:
            force_authenticate(request, user=user)
        response = PostListView.as_view()(request)
        response.render()
        return response

    def test_list_unauthenticated_only_public_and_friends(self):
        resp = self._call_list()
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertTrue(data.get("success"))
        ids = self._extract_ids(data)
        # 未登录仅 public
        self.assertCountEqual(ids, [self.p0_public.id, self.p1_public.id])
        self.assertNotIn(self.p0_private.id, ids)
        self.assertNotIn(self.p1_private.id, ids)
        self.assertNotIn(self.p1_friends.id, ids)

    def test_list_authenticated_can_see_self_private(self):
        resp = self._call_list(user=self.user0)
        self.assertEqual(resp.status_code, 200)
        data = resp.data
        self.assertTrue(data.get("success"))
        ids = self._extract_ids(data)
        # user0 能看到自己的 private，同时能看到他人 public/friends
        self.assertIn(self.p0_private.id, ids)
        self.assertIn(self.p0_public.id, ids)
        self.assertIn(self.p0_friends.id, ids)
        # 未成好友前只应看到对方公开，不含 friends/private
        self.assertIn(self.p1_public.id, ids)
        self.assertNotIn(self.p1_private.id, ids)
        self.assertNotIn(self.p1_friends.id, ids)
        # 成为好友后可见对方 friends
        Friendship.objects.create(from_user=self.user0, to_user=self.user1, status="accepted")
        resp2 = self._call_list(user=self.user0)
        ids2 = self._extract_ids(resp2.data)
        self.assertIn(self.p1_public.id, ids2)
        self.assertIn(self.p1_friends.id, ids2)
        self.assertNotIn(self.p1_private.id, ids2)
