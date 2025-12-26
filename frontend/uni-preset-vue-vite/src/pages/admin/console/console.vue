<template>
  <view class="admin-page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <scroll-view scroll-y class="scroll">
      <view class="header">
        <view>
          <text class="title">管理控制台</text>
          <text class="subtitle">快速总览 · 用户与内容</text>
        </view>
        <view class="actions">
          <button size="mini" class="btn" @tap="reload">刷新</button>
          <button size="mini" class="btn danger" @tap="logout">退出</button>
        </view>
      </view>

      <view class="cards">
        <view class="card">
          <text class="card-label">用户总数</text>
          <text class="card-value">{{ metrics.users }}</text>
        </view>
        <view class="card">
          <text class="card-label">动态总数</text>
          <text class="card-value">{{ metrics.posts }}</text>
        </view>
        <view class="card">
          <text class="card-label">今日新增</text>
          <text class="card-value">{{ metrics.today }}</text>
        </view>
      </view>

      <view class="panel">
        <view class="panel-header">
          <text class="panel-title">用户管理</text>
          <view class="panel-actions">
            <input class="input" v-model="userKeyword" placeholder="搜索用户名/ID" />
            <button size="mini" class="btn" @tap="fetchUsers">查询</button>
          </view>
        </view>
        <view v-if="users.length === 0" class="empty">暂无数据</view>
        <view v-else class="list">
          <view class="row" v-for="u in users" :key="u.id">
            <text class="cell w120">ID: {{ u.id }}</text>
            <text class="cell">{{ u.username }}</text>
            <text class="cell">{{ u.email || '无邮箱' }}</text>
            <text class="cell">{{ u.is_active ? '启用' : '禁用' }}</text>
            <button size="mini" class="btn danger" @tap="disableUser(u)" v-if="u.is_active">禁用</button>
            <button size="mini" class="btn" @tap="enableUser(u)" v-else>启用</button>
          </view>
        </view>
      </view>

      <view class="panel">
        <view class="panel-header">
          <text class="panel-title">内容管理</text>
          <view class="panel-actions">
            <input class="input" v-model="postKeyword" placeholder="按用户/标签/关键词" />
            <button size="mini" class="btn" @tap="fetchPosts">查询</button>
          </view>
        </view>
        <view v-if="posts.length === 0" class="empty">暂无动态</view>
        <view v-else class="list">
          <view class="row" v-for="p in posts" :key="p.id">
            <view class="col-main">
              <text class="cell strong">#{{ p.id }} {{ p.name || p.user?.username || '匿名' }}</text>
              <text class="cell">{{ p.text || '(无文本)' }}</text>
              <text class="cell">可见性: {{ p.visibility || 'public' }} · 点赞 {{ p.likes }} · 评论 {{ p.comments }}</text>
            </view>
            <button size="mini" class="btn danger" @tap="deletePost(p)">删除</button>
          </view>
        </view>
      </view>

    </scroll-view>
  </view>
</template>

<script>
import { fetchMe, adminListUsers, adminToggleUser, adminListPosts, adminDeletePost } from '@/services/api'

export default {
  data() {
    return {
      statusBarHeight: 0,
      metrics: { users: '--', posts: '--', today: '--' },
      users: [],
      posts: [],
      userKeyword: '',
      postKeyword: ''
    }
  },
  onLoad() {
    this.setStatusBar()
    this.reload()
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
    logout() {
      uni.removeStorageSync('auth_token')
      uni.reLaunch({ url: '/pages/admin/login/login' })
    },
    async reload() {
      await Promise.all([this.fetchMe(), this.fetchUsers(), this.fetchPosts()])
    },
    async fetchMe() {
      try {
        const me = await fetchMe()
        if (me?.username) {
          this.metrics.users = me.total_users || '--'
          this.metrics.posts = me.total_posts || '--'
          this.metrics.today = me.today_posts || '--'
        }
      } catch (e) {
        // ignore
      }
    },
    async fetchUsers() {
      try {
        const resp = await adminListUsers({ search: this.userKeyword, page: 1, pageSize: 20 })
        const raw = resp?.results || resp?.data || resp
        this.users = Array.isArray(raw) ? raw : (raw?.results || [])
      } catch (e) {
        this.users = []
      }
    },
    async fetchPosts() {
      try {
        const resp = await adminListPosts({ keyword: this.postKeyword, page: 1, pageSize: 20 })
        const raw = resp?.results || resp?.data || resp
        this.posts = Array.isArray(raw) ? raw : (raw?.results || [])
      } catch (e) {
        this.posts = []
      }
    },
    async disableUser(u) {
      await this.toggleUser(u, false)
    },
    async enableUser(u) {
      await this.toggleUser(u, true)
    },
    async toggleUser(u, isActive) {
      try {
        await adminToggleUser({ userId: u.id, is_active: isActive })
        uni.showToast({ title: isActive ? '已启用' : '已禁用', icon: 'success' })
        this.fetchUsers()
      } catch (e) {
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    deletePost(p) {
      uni.showModal({
        title: '确认删除',
        content: `删除动态 #${p.id}?`,
        success: async (res) => {
          if (res.confirm) {
            try {
              await adminDeletePost({ postId: p.id })
              uni.showToast({ title: '已删除', icon: 'success' })
              this.fetchPosts()
            } catch (e) {
              uni.showToast({ title: '删除失败', icon: 'none' })
            }
          }
        }
      })
    }
  }
}
</script>

<style scoped>
.admin-page {
  width: 100%;
  height: 100vh;
  background: #f5f7fb;
  box-sizing: border-box;
}
.scroll {
  width: 100%;
  height: 100%;
  padding: 24rpx;
  box-sizing: border-box;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20rpx;
}
.title {
  font-size: 34rpx;
  font-weight: 700;
  color: #2d2f33;
}
.subtitle {
  font-size: 24rpx;
  color: #888;
}
.actions { display: flex; gap: 12rpx; }
.btn {
  background: linear-gradient(135deg, #5b8def 0%, #6f7dec 100%);
  color: #fff;
  border-radius: 12rpx;
  padding: 12rpx 20rpx;
}
.btn.danger { background: linear-gradient(135deg, #f56565 0%, #f87171 100%); }
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16rpx;
  margin-bottom: 24rpx;
}
.card {
  background: #fff;
  border-radius: 18rpx;
  padding: 24rpx;
  box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.04);
}
.card-label { font-size: 24rpx; color: #666; }
.card-value { font-size: 40rpx; font-weight: 700; color: #2d2f33; }
.panel {
  background: #fff;
  border-radius: 18rpx;
  padding: 20rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 12rpx 32rpx rgba(0,0,0,0.04);
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
  margin-bottom: 12rpx;
}
.panel-title { font-size: 30rpx; font-weight: 600; }
.panel-actions { display: flex; gap: 12rpx; align-items: center; }
.input {
  min-width: 240rpx;
  padding: 16rpx;
  border: 1rpx solid #e5e7eb;
  border-radius: 12rpx;
  background: #f9fafb;
  font-size: 26rpx;
}
.list { display: flex; flex-direction: column; gap: 12rpx; }
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx;
  border: 1rpx solid #f0f2f5;
  border-radius: 12rpx;
  background: #fafbff;
}
.col-main { flex: 1; display: flex; flex-direction: column; gap: 6rpx; }
.cell { font-size: 24rpx; color: #444; }
.cell.strong { font-weight: 600; }
.empty { padding: 20rpx; color: #888; font-size: 26rpx; }
.w120 { min-width: 120rpx; }
</style>
