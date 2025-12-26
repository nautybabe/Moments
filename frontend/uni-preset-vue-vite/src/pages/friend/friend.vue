<template>
  <view class="page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <view class="nav-bar">
      <view class="nav-left" @tap="goBack">
        <text class="icon">←</text>
        <text class="nav-text">返回</text>
      </view>
      <text class="nav-title">好友列表</text>
      <view class="nav-right" @tap="goSearch">
        <text class="icon">＋</text>
      </view>
    </view>

    <scroll-view scroll-y class="scroll-area">
      <view class="section">
        <view class="section-header">
          <text class="section-title">我的好友</text>
          <text class="section-count">{{ friends.length }} 人</text>
        </view>
        <view v-if="friends.length === 0" class="empty">暂无好友，点击右上角去添加</view>
        <view v-for="f in friends" :key="f.id" class="card">
          <image class="avatar" :src="f.avatar || defaultAvatar" mode="aspectFill" />
          <view class="card-meta">
            <text class="name">{{ f.nickname || f.username || '未命名用户' }}</text>
            <text class="sub">ID: {{ f.id }}</text>
            <text class="sub" v-if="f.signature">签名: {{ f.signature }}</text>
          </view>
        </view>
      </view>

      <view class="section">
        <view class="section-header">
          <text class="section-title">待处理申请</text>
          <text class="section-count">{{ friendRequests.length }} 条</text>
        </view>
        <view v-if="friendRequests.length === 0" class="empty">暂无待处理申请</view>
        <view v-for="req in friendRequests" :key="req.id" class="card">
          <image class="avatar" :src="req.avatar || defaultAvatar" mode="aspectFill" />
          <view class="card-meta">
            <text class="name">{{ req.nickname || req.from_user_name || '用户 ' + req.from_user }}</text>
            <text class="sub">申请ID: {{ req.id }}</text>
            <text class="sub" v-if="req.signature">签名: {{ req.signature }}</text>
          </view>
          <view class="actions">
            <button size="mini" class="btn primary" :disabled="loading" @tap="handleRespond(req, 'accept')">同意</button>
            <button size="mini" class="btn ghost" :disabled="loading" @tap="handleRespond(req, 'reject')">拒绝</button>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import {
  listFriendsApi,
  listFriendRequestsApi,
  respondFriendRequestApi
} from '@/services/api'

export default {
  data() {
    return {
      statusBarHeight: 0,
      friends: [],
      friendRequests: [],
      loading: false,
      defaultAvatar: 'https://picsum.photos/200'
    }
  },
  onLoad() {
    this.setStatusBar()
    this.loadData()
  },
  methods: {
    setStatusBar() {
      try {
        const info = uni.getSystemInfoSync()
        this.statusBarHeight = info.statusBarHeight || 0
      } catch (e) {
        this.statusBarHeight = 0
      }
    },
    async loadData() {
      this.loading = true
      try {
        const [fRes, rRes] = await Promise.all([
          listFriendsApi(),
          listFriendRequestsApi()
        ])
        const friendsRaw = fRes?.data?.friends || []
        this.friends = friendsRaw.map(f => ({
          ...f,
          avatar: f.avatar || f.profile?.avatar || this.defaultAvatar
        }))
        // backend returns {requests: []}
        const reqRaw = rRes?.data?.requests || []
        this.friendRequests = reqRaw.map(r => ({
          ...r,
          avatar: r.avatar || r.profile?.avatar || this.defaultAvatar
        }))
      } catch (e) {
        uni.showToast({ title: '获取好友数据失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    async handleRespond(req, action) {
      if (this.loading) return
      this.loading = true
      try {
        const resp = await respondFriendRequestApi({ requestId: req.id, action })
        if (resp?.success) {
          uni.showToast({
            title: action === 'accept' ? '已同意' : '已拒绝',
            icon: 'success'
          })
          this.loadData()
        } else {
          uni.showToast({ title: resp?.message || '操作失败', icon: 'none' })
          this.loading = false
        }
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
        this.loading = false
      }
    },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        uni.switchTab({ url: '/pages/mine/mine' })
      }
    },
    goSearch() {
      uni.navigateTo({ url: '/pages/search/search' })
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  background: #f5f7fb;
  display: flex;
  flex-direction: column;
}

.nav-bar {
  height: 88rpx;
  padding: 0 24rpx;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.1);
}

.nav-left, .nav-right {
  display: flex;
  align-items: center;
  gap: 8rpx;
  min-width: 120rpx;
}

.nav-right { justify-content: flex-end; }

.nav-title {
  font-size: 32rpx;
  font-weight: 700;
}

.icon {
  font-size: 32rpx;
}

.nav-text {
  font-size: 28rpx;
}

.scroll-area {
  flex: 1;
  padding: 24rpx 24rpx 40rpx;
  box-sizing: border-box;
}

.section {
  margin-bottom: 32rpx;
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16rpx;
}

.section-title {
  font-size: 30rpx;
  color: #333;
  font-weight: 700;
}

.section-count {
  font-size: 24rpx;
  color: #999;
}

.empty {
  background: #fff;
  border-radius: 18rpx;
  padding: 28rpx;
  color: #999;
  font-size: 26rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.04);
}

.card {
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 18rpx;
  padding: 20rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
}

.avatar {
  width: 96rpx;
  height: 96rpx;
  border-radius: 50%;
  background: #f0f0f0;
  margin-right: 18rpx;
}

.card-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
}

.sub {
  font-size: 24rpx;
  color: #888;
}

.actions {
  display: flex;
  gap: 12rpx;
}

.btn {
  border-radius: 999rpx;
  padding: 0 20rpx;
  border: none;
}

.btn.primary {
  background: linear-gradient(135deg, #18a058 0%, #34d399 100%);
  color: #fff;
}

.btn.ghost {
  background: #fff;
  border: 1rpx solid #e5e7eb;
  color: #666;
}
</style>
