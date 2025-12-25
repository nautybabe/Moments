<template>
  <view class="page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <scroll-view scroll-y class="scroll-area">
    <view class="profile-card">
      <image class="avatar big" :src="profile.avatar" mode="aspectFill" />
      <view class="profile-meta">
        <text class="name">{{ profile.nickname }}</text>
        <text class="desc">{{ profile.signature }}</text>
      </view>
      <view class="stats">
        <view class="stat">
          <text class="stat-num">{{ myStats.posts }}</text>
          <text class="stat-label">动态</text>
        </view>
      </view>
      <view class="profile-actions">
        <button size="mini" class="profile-btn primary" @tap="handlePublish">发动态</button>
        <button size="mini" class="profile-btn" @tap="handleSettings">设置</button>
      </view>
    </view>

    <view class="section-title">我的动态</view>
    <view class="post-card" v-for="item in myPosts" :key="item.id">
      <view class="post-header">
        <image class="avatar" :src="item.avatar || profile.avatar" mode="aspectFill" />
        <view class="meta">
          <text class="name">{{ item.name || profile.nickname }}</text>
          <text class="time">{{ item.time }}</text>
        </view>
        <!-- 删除按钮 -->
        <view class="delete-btn" @tap="handleDelete(item)">删除</view>
      </view>
      
      <view class="post-content">
        <text class="text">{{ item.text }}</text>
        <!-- 标签显示 -->
        <view class="tags-row" v-if="item.tags && item.tags.length">
          <view class="tag" v-for="tag in item.tags" :key="tag">#{{ tag }}</view>
        </view>
      </view>
      
      <!-- 1. 纯图片帖子 -->
      <view class="media-grid" v-if="item.type === 'image' && item.media && item.media.length">
        <image
          v-for="(img, idx) in item.media"
          :key="idx"
          class="media-img"
          :src="img"
          mode="aspectFill"
          @tap.stop="previewImage(item.media, idx)"
        />
      </view>

      <!-- 2. 视频帖子：视频与附图并列展示 -->
      <template v-else-if="item.type === 'video'">
        <view class="video-wrapper" v-if="item.media && item.media.length">
          <video
            class="video-player"
            :src="item.media[0]"
            :poster="item.poster || item.media[1] || ''"
            controls
            :enable-progress-gesture="true"
            show-progress="true"
            object-fit="cover"
          />
        </view>
        <view class="media-grid" v-if="item.extraImages && item.extraImages.length">
          <image
            v-for="(img, idx) in item.extraImages"
            :key="idx"
            class="media-img"
            :src="img"
            mode="aspectFill"
            @tap.stop="previewImage(item.extraImages, idx)"
          />
        </view>
      </template>

      <!-- 3. 兜底显示 -->
      <view class="media-grid" v-else-if="item.type !== 'image' && item.type !== 'video' && item.media && item.media.length">
        <image
          v-for="(img, idx) in item.media"
          :key="idx"
          class="media-img"
          :src="img"
          mode="aspectFit"
        />
      </view>
      
      <view class="actions-row">
        <view class="action" @tap="toggleLike(item)">
          <text>{{ item.liked ? '❤️' : '🤍' }}</text>
          <text class="action-text">{{ item.likes || 0 }}</text>
        </view>
        <view class="action" @tap="handleComment(item)">
          <text>💬</text>
          <text class="action-text">{{ item.comments || 0 }}</text>
        </view>
      </view>
    </view>

    <!-- 删除确认弹窗 -->
    <view class="delete-modal" v-if="showDeleteModal" @tap="closeDeleteModal">
      <view class="delete-content" @tap.stop>
        <view class="delete-header">
          <text class="delete-title">删除动态</text>
        </view>
        <text class="delete-text">确定要删除这条动态吗？删除后将无法恢复。</text>
        <view class="delete-actions">
          <button class="delete-btn cancel" @tap="closeDeleteModal">取消</button>
          <button class="delete-btn confirm" @tap="confirmDelete">确认删除</button>
        </view>
      </view>
    </view>

    <!-- 评论弹窗 -->
    <view class="comment-modal" v-if="showCommentModal" @tap="closeCommentModal">
      <view class="comment-content" @tap.stop>
        <view class="comment-header">
          <text class="comment-title">评论 ({{ currentPostComments.length }})</text>
          <text class="close-btn" @tap="closeCommentModal">✕</text>
        </view>
        
        <scroll-view class="comment-list" scroll-y>
          <view v-if="currentPostComments.length === 0" class="empty-comments">
            <text>暂无评论，快来发表第一条评论吧～</text>
          </view>
          <view 
            class="comment-item" 
            v-for="comment in currentPostComments" 
            :key="comment.id"
          >
            <image class="comment-avatar" :src="comment.avatar" mode="aspectFill" />
            <view class="comment-body">
              <view class="comment-info">
                <text class="comment-name">{{ comment.name }}</text>
                <text class="comment-time">{{ comment.time }}</text>
              </view>
              <text class="comment-text">{{ comment.content }}</text>
            </view>
          </view>
        </scroll-view>

        <view class="comment-input-bar">
          <input
            class="comment-input"
            type="text"
            v-model="newCommentText"
            placeholder="说点什么..."
            confirm-type="send"
            @confirm="submitComment"
          />
          <button 
            class="send-btn" 
            :disabled="!newCommentText.trim() || submittingComment"
            @tap="submitComment"
          >
            {{ submittingComment ? '发送中...' : '发送' }}
          </button>
        </view>
      </view>
    </view>
  </scroll-view>
  </view>
</template>

<script>
import { fetchMe, fetchMyPosts, deletePostApi } from '@/services/api'
export default {
  data() {
    return {
      statusBarHeight: 0,
      profile: {
        avatar: 'https://picsum.photos/200',
        nickname: '小程序用户',
        signature: '记录生活 · 分享精彩'
      },
      myPosts: [],
      myStats: {
        posts: 0
      },
      showDeleteModal: false,
      deletePostId: null,
      showCommentModal: false,
      currentPostId: null,
      currentPostComments: [],
      newCommentText: '',
      submittingComment: false,
      commentsData: {}
    }
  },
  onLoad() {
    this.setStatusBar()
    this.loadProfileFromStorage()
    // 监听发布事件，把自己的帖子加入列表
    this.__newMyPostHandler = (payload = {}) => {
      if (payload.myPost) {
        const dedupMedia = Array.from(new Set(payload.myPost.media || []))
        this.myPosts.unshift({
          ...payload.myPost,
          id: payload.myPost.id || Date.now(),
          media: dedupMedia,
          likes: payload.myPost.likes || 0,
          comments: payload.myPost.comments || 0,
          liked: false
        })
        // 更新统计
        this.myStats.posts = (this.myStats.posts || 0) + 1
      }
    }
    uni.$on('newPostPublished', this.__newMyPostHandler)

    // 监听个人资料更新
    this.__profileUpdatedHandler = async (payload = {}) => {
      const { avatar, nickname, signature } = payload
      if (avatar) this.profile.avatar = avatar
      if (nickname) this.profile.nickname = nickname
      if (signature !== undefined) this.profile.signature = signature
      // 同步已有列表的头像和昵称
      this.myPosts = this.myPosts.map(p => ({
        ...p,
        avatar: avatar || p.avatar || this.profile.avatar,
        name: nickname || p.name || this.profile.nickname
      }))
    }
    uni.$on('profileUpdated', this.__profileUpdatedHandler)
  },
  onShow() {
    this.setStatusBar()
    this.loadProfileFromStorage()
    this.pullProfile()
    this.loadMyPosts()
  },
  onUnload() {
    if (this.__newMyPostHandler) {
      uni.$off('newPostPublished', this.__newMyPostHandler)
      this.__newMyPostHandler = null
    }
    if (this.__profileUpdatedHandler) {
      uni.$off('profileUpdated', this.__profileUpdatedHandler)
      this.__profileUpdatedHandler = null
    }
  },
  methods: {
    formatTime(ts) {
      if (!ts) return ''
      const date = new Date(ts)
      const diff = Date.now() - date.getTime()
      const sec = Math.floor(diff / 1000)
      if (sec < 60) return '刚刚'
      const min = Math.floor(sec / 60)
      if (min < 60) return `${min}分钟前`
      const hour = Math.floor(min / 60)
      if (hour < 24) return `${hour}小时前`
      const day = Math.floor(hour / 24)
      if (day < 7) return `${day}天前`
      return date.toLocaleDateString()
    },
    setStatusBar() {
      try {
        const info = uni.getSystemInfoSync()
        this.statusBarHeight = info.statusBarHeight || 0
      } catch (e) {
        this.statusBarHeight = 0
      }
    },
    loadProfileFromStorage() {
      try {
        const stored = uni.getStorageSync('current_user') || {}
        const profileData = stored.profile || {}
        const nickname = stored.username || stored.nickname || '小程序用户'

        const signature = profileData.signature || stored.signature || '记录生活 · 分享精彩'
        const avatar = profileData.avatar || stored.avatar || this.profile.avatar
        this.profile.nickname = nickname
        this.profile.signature = signature
        this.profile.avatar = avatar
        // 同步已有列表显示
        this.myPosts = this.myPosts.map(p => ({
          ...p,
          name: nickname,
          avatar: avatar || p.avatar,
          likes: p.likes || 0,
          comments: p.comments || 0
        }))
      } catch (e) {
        // 静默失败
      }
    },
    async pullProfile() {
      try {
        const data = await fetchMe()
        // 更新本地缓存和界面
        uni.setStorageSync('current_user', data)
        this.profile.nickname = data.username || data.nickname || '小程序用户'
        this.profile.signature = data.profile.signature || data.signature || '记录生活 · 分享精彩'
        this.profile.avatar = data.profile.avatar || data.avatar || this.profile.avatar
        // 同步已有列表的头像/昵称
        this.myPosts = this.myPosts.map(p => ({
          ...p,
          avatar: this.profile.avatar,
          name: this.profile.nickname,
          likes: p.likes || 0,
          comments: p.comments || 0,
          liked: p.liked || false
        }))
      } catch (e) {
        // 静默失败
      }
    },
    async loadMyPosts() {
      try {
        const list = await fetchMyPosts()
        this.myPosts = (list || []).map(item => {
          const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

          const normalizeUrl = (url) => {
            if (!url) return ''
            const fixedSlashes = url.replace(/\\/g, '/')
            if (/^https?:\/\//i.test(fixedSlashes)) return fixedSlashes
            if (fixedSlashes.startsWith('/media/')) return `${API_BASE}${fixedSlashes}`
            return fixedSlashes
          }

          const mediaList = (item.media || [])
            .filter(Boolean)
            .map(normalizeUrl)
          // 去重，避免重复图片
          const dedupedMediaList = Array.from(new Set(mediaList))

          let type = item.type || (dedupedMediaList.length > 0 ? 'image' : 'text')
          if (type === 'text' && dedupedMediaList.length > 0) type = 'image'
          const created = item.created_at || item.created_time || ''

          let poster = item.poster ? normalizeUrl(item.poster) : ''
          let mediaForRender = dedupedMediaList
          let extraImages = []

          if (type === 'video') {
            const imageRegex = /\.(png|jpe?g|webp|gif)$/i
            let videoUrl = ''
            const images = []
            dedupedMediaList.forEach(url => {
              if (!url) return
              const isImage = imageRegex.test(url)
              const looksLikeVideo = url.includes('/uploads/videos/') || /\.mp4$/i.test(url)
              if (!videoUrl && (looksLikeVideo || !isImage)) {
                videoUrl = url
              } else if (isImage) {
                images.push(url)
              }
            })
            if (!videoUrl && images.length) {
              // 实际没有视频，用图片渲染
              type = 'image'
              mediaForRender = images
              extraImages = []
              poster = ''
            } else {
              // 仅使用后端返回的 poster，避免把附图当成封面
              if (!poster || poster.includes('/uploads/videos/')) {
                poster = ''
              }
              mediaForRender = videoUrl ? [videoUrl] : []
              // 附图去重展示
              extraImages = Array.from(new Set(images))
            }
          } else {
            // 纯图片帖子，直接使用去重后的列表
            extraImages = []
            mediaForRender = dedupedMediaList
          }

          return {
            id: item.id,
            time: item.time || this.formatTime(created),
            text: item.text || '',
            type,
            media: mediaForRender,
            poster,
            extraImages,
            likes: item.likes_count || item.likes || 0,
            comments: item.comments_count || item.comments || 0,
            liked: item.is_liked || false,
            avatar: item.user?.profile?.avatar || this.profile.avatar,
            name: item.user?.username || this.profile.nickname,
            tags: item.tags || []
          }
        })
        this.myStats.posts = this.myPosts.length
      } catch (e) {
        // 静默失败
      }
    },
    handlePublish() {
      // 跳转到发动态页面
      uni.navigateTo({
        url: '/pages/publish/publish'
      })
    },
    handleSettings() {
      // 跳转到设置页面
      uni.navigateTo({
        url: '/pages/settings/settings'
      })
    },

    // 删除功能相关方法
    handleDelete(item) {
      this.deletePostId = item.id
      this.showDeleteModal = true
    },
    closeDeleteModal() {
      this.showDeleteModal = false
      this.deletePostId = null
    },
    confirmDelete() {
      if (!this.deletePostId) return
      
      // 调用后端删除API
      deletePostApi({ postId: this.deletePostId })
        .then(response => {
          if (response.success) {
            // 从前端数组中移除
            const index = this.myPosts.findIndex(item => item.id === this.deletePostId)
            if (index !== -1) {
              this.myPosts.splice(index, 1)
              // 更新帖子数量统计
              this.myStats.posts = Math.max(0, this.myStats.posts - 1)
              
              // 删除对应的评论数据
              delete this.commentsData[this.deletePostId]
              
              // 如果当前打开的评论弹窗是删除的帖子，关闭评论弹窗
              if (this.currentPostId === this.deletePostId) {
                this.closeCommentModal()
              }
            }
            
            uni.showToast({
              title: '删除成功',
              icon: 'success'
            })
          } else {
            uni.showToast({
              title: response.message || '删除失败',
              icon: 'none'
            })
          }
        })
        .catch(error => {
          console.error('删除失败:', error)
          uni.showToast({
            title: '删除失败，请重试',
            icon: 'none'
          })
        })
        .finally(() => {
          this.closeDeleteModal()
        })
    },
    
    toggleLike(item) {
      item.liked = !item.liked
      item.likes += item.liked ? 1 : -1
      this.$forceUpdate()
    },
    handleComment(item) {
      this.currentPostId = item.id
      this.currentPostComments = this.commentsData[item.id] || []
      this.showCommentModal = true
      this.newCommentText = ''
    },
    closeCommentModal() {
      this.showCommentModal = false
      this.currentPostId = null
      this.currentPostComments = []
      this.newCommentText = ''
    },
    async submitComment() {
      const content = this.newCommentText.trim()
      if (!content) {
        uni.showToast({ title: '请输入评论内容', icon: 'none' })
        return
      }

      this.submittingComment = true

      setTimeout(() => {
        const newComment = {
          id: Date.now(),
          name: '我',
          avatar: 'https://picsum.photos/200',
          content: content,
          time: '刚刚'
        }

        if (!this.commentsData[this.currentPostId]) {
          this.commentsData[this.currentPostId] = []
        }
        this.commentsData[this.currentPostId].unshift(newComment)
        this.currentPostComments = this.commentsData[this.currentPostId]

        const myPost = this.myPosts.find(p => p.id === this.currentPostId)
        if (myPost) {
          myPost.comments = (myPost.comments || 0) + 1
        }

        this.newCommentText = ''
        this.submittingComment = false
        uni.showToast({ title: '评论成功', icon: 'success' })
      }, 500)
    },
    previewImage(urls, current = 0) {
      if (!urls || !urls.length) return
      uni.previewImage({
        urls,
        current
      })
    }
  }
}
</script>

<style scoped>
.page {
  width: 100%;
  height: 100vh;
  background: #f5f7fb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-sizing: border-box;
}

.scroll-area {
  width: 100%;
  padding: 20rpx 24rpx 40rpx;
  box-sizing: border-box;
  flex: 1;
  height: 100vh;
}

.section-title {
  margin: 20rpx 0;
  color: #666;
  font-size: 28rpx;
}

.profile-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  margin: 20rpx 0 10rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  box-sizing: border-box;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  margin-right: 16rpx;
  background: #f2f2f2;
}

.avatar.big {
  width: 120rpx;
  height: 120rpx;
}

.profile-meta {
  text-align: center;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
  display: block;
  margin-bottom: 8rpx;
}

.desc {
  color: #888;
  font-size: 26rpx;
  display: block;
}

.stats {
  display: flex;
  padding: 16rpx 20rpx;
  background: #f6f7fb;
  border-radius: 18rpx;
  margin-top: 10rpx;
  gap: 24rpx;
}

.stat-num {
  font-size: 34rpx;
  color: #333;
  font-weight: 700;
  display: block;
  text-align: center;
}

.stat-label {
  font-size: 24rpx;
  color: #888;
  display: block;
  text-align: center;
}

.profile-actions {
  display: flex;
  gap: 12rpx;
}

.profile-btn {
  border-radius: 999rpx;
  padding: 0 20rpx;
  background: #f4f5fb;
  color: #555;
  border: none;
}

.profile-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 24rpx;
  box-sizing: border-box;
  position: relative;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
  position: relative;
}

.meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.time {
  font-size: 24rpx;
  color: #999;
}

/* 删除按钮样式 */
.delete-btn {
  padding: 8rpx 20rpx;
  background: #fff;
  color: #ff4444;
  font-size: 24rpx;
  border-radius: 20rpx;
  border: 1rpx solid #ff4444;
  margin-left: 16rpx;
  white-space: nowrap;
}

.delete-btn:hover {
  background: #ffeeee;
}

.post-content {
  margin-bottom: 16rpx;
}

.text {
  color: #444;
  font-size: 30rpx;
  line-height: 1.6;
  margin-bottom: 16rpx;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin-bottom: 16rpx;
}

.tag {
  padding: 6rpx 12rpx;
  background: #f0f0f0;
  color: #666;
  font-size: 24rpx;
  border-radius: 12rpx;
  white-space: nowrap;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10rpx;
  margin-top: 10rpx;
  margin-bottom: 12rpx;
  width: 100%;
  box-sizing: border-box;
}

.media-img {
  width: 100%;
  height: 220rpx;
  border-radius: 16rpx;
  background: #f2f2f2;
  object-fit: cover;
  box-sizing: border-box;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 10rpx;
}

.action {
  display: flex;
  align-items: center;
  gap: 8rpx;
  color: #666;
  font-size: 26rpx;
}

.action-text {
  color: #666;
}

/* 删除确认弹窗样式 */
.delete-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1001;
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.3s ease;
}

.delete-content {
  width: 80%;
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx 32rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: scaleIn 0.3s ease;
}

@keyframes scaleIn {
  from {
    transform: scale(0.8);
    opacity: 0;
  }
  to {
    transform: scale(1);
    opacity: 1;
  }
}

.delete-header {
  margin-bottom: 20rpx;
}

.delete-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #333;
}

.delete-text {
  font-size: 28rpx;
  color: #666;
  text-align: center;
  margin-bottom: 40rpx;
  line-height: 1.6;
}

.delete-actions {
  display: flex;
  gap: 20rpx;
  width: 100%;
}

.delete-actions .delete-btn {
  flex: 1;
  padding: 20rpx 0;
  border-radius: 12rpx;
  font-size: 28rpx;
  border: none;
}

.delete-actions .cancel {
  background: #f5f5f5;
  color: #666;
}

.delete-actions .confirm {
  background: #ff4444;
  color: #fff;
}

/* 评论弹窗 */
.comment-modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.comment-content {
  width: 100%;
  max-height: 80vh;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

.comment-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 32rpx;
  border-bottom: 1rpx solid #eee;
}

.comment-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.close-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36rpx;
  color: #999;
  border-radius: 50%;
  background: #f5f5f5;
}

.comment-list {
  flex: 1;
  padding: 20rpx 32rpx;
  min-height: 200rpx;
  max-height: 50vh;
}

.empty-comments {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}

.comment-item {
  display: flex;
  margin-bottom: 32rpx;
}

.comment-avatar {
  width: 64rpx;
  height: 64rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #f2f2f2;
  flex-shrink: 0;
}

.comment-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.comment-info {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 8rpx;
}

.comment-name {
  font-size: 28rpx;
  color: #333;
  font-weight: 600;
}

.comment-time {
  font-size: 24rpx;
  color: #999;
}

.comment-text {
  font-size: 28rpx;
  color: #444;
  line-height: 1.6;
  word-break: break-all;
}

.comment-input-bar {
  display: flex;
  align-items: center;
  padding: 20rpx 32rpx;
  border-top: 1rpx solid #eee;
  background: #fff;
  gap: 16rpx;
}

.comment-input {
  flex: 1;
  padding: 16rpx 24rpx;
  background: #f5f5f5;
  border-radius: 999rpx;
  font-size: 28rpx;
  color: #333;
}

.send-btn {
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 500;
}

.send-btn[disabled] {
  opacity: 0.5;
  background: #ccc;
}
</style>