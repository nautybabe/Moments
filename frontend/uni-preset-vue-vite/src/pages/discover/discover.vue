<template>
  <view class="page" :style="{ paddingTop: topPadding + 'px' }">
    <scroll-view scroll-y class="scroll-area" :style="{ height: scrollHeight + 'px' }">
    <view class="search-row">
      <view class="search-box" @tap="goToSearch">
        <text class="search-icon">🔍</text>
        <text class="search-placeholder">搜索好友、话题或内容</text>
      </view>
      <view class="notify-btn" @tap="handleNotify">
        <text>🔔</text>
        <view class="badge" v-if="notifyCount > 0">{{ notifyCount }}</view>
      </view>
    </view>
    

    <view class="section-title">好友动态</view>
    <view class="post-card" v-for="item in posts" :key="item.id">
      <view class="post-header">
        <image class="avatar" :src="item.avatar" mode="aspectFill" />
        <view class="meta">
          <text class="name">{{ item.name }}</text>
          <text class="time">{{ item.time }}</text>
        </view>
        <view class="tag-wrap">
          <text class="tag" v-if="item.tag">{{ item.tag }}</text>
          <text class="visibility" :class="`vis-${item.visibility || 'public'}`">
            {{ visLabel(item.visibility) }}
          </text>
        </view>
      </view>

      <view class="text" v-if="item.text">{{ item.text }}</view>

      <view class="media-grid" v-if="item.type === 'image'">
        <image
          v-for="(img, idx) in item.mediaImages"
          :key="idx"
          class="media-img"
          :src="img"
          mode="aspectFill"
        />
      </view>

      <view class="media-video" v-if="item.type === 'video'">
        <video
          :src="item.videoSrc"
          :poster="item.poster"
          controls
          autoplay="false"
          show-center-play-btn
          object-fit="cover"
        />
      </view>
      <!-- 视频下方的图片（如有） -->
      <view class="media-grid" v-if="item.type === 'video' && item.mediaImages && item.mediaImages.length">
        <image
          v-for="(img, idx) in item.mediaImages"
          :key="idx"
          class="media-img"
          :src="img"
          mode="aspectFill"
        />
      </view>

      <view class="tag-rating-row" v-if="item.tags && item.tags.length">
        <view class="tags">
          <text class="tag-chip" v-for="tag in item.tags" :key="tag">#{{ tag }}</text>
        </view>
      </view>

      <view class="actions-row">
        <view class="action" @tap="toggleLike(item)">
          <text>{{ item.liked ? '❤️' : '🤍' }}</text>
          <text class="action-text">{{ item.likes }}</text>
        </view>
        <view class="action" @tap="handleComment(item)">
          <text>💬</text>
          <text class="action-text">{{ item.comments }}</text>
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

    <!-- 消息通知弹窗 -->
    <view class="notify-modal" v-if="showNotifyModal" @tap="closeNotifyModal">
      <view class="notify-content" @tap.stop>
        <view class="notify-header">
          <text class="notify-title">消息通知</text>
          <view class="notify-actions">
            <text class="mark-read-btn" @tap="markAllAsRead" v-if="unreadCount > 0">
              全部已读
            </text>
            <text class="close-btn" @tap="closeNotifyModal">✕</text>
          </view>
        </view>
        
        <scroll-view class="notify-list" scroll-y>
          <view v-if="notifications.length === 0" class="empty-notify">
            <text>暂无消息</text>
          </view>
          <view 
            class="notify-item" 
            :class="{ unread: !notification.read }"
            v-for="notification in notifications" 
            :key="notification.id"
            @tap="handleNotifyClick(notification)"
          >
            <image class="notify-avatar" :src="notification.avatar" mode="aspectFill" />
            <view class="notify-body">
              <view class="notify-info">
                <text class="notify-name">{{ notification.name }}</text>
                <text class="notify-time">{{ notification.time }}</text>
              </view>
              <view class="notify-message">
                <text class="notify-icon">{{ getNotifyIcon(notification.type) }}</text>
                <text class="notify-text">{{ getNotifyText(notification) }}</text>
              </view>
              <view class="notify-post-preview" v-if="notification.postText">
                <text class="preview-text">{{ notification.postText }}</text>
              </view>
            </view>
            <view class="unread-dot" v-if="!notification.read"></view>
          </view>
        </scroll-view>
      </view>
    </view>
  </scroll-view>
  </view>
</template>

<script>
import { getPostsApi, likePostApi, getCommentsApi, createCommentApi, getNotificationsApi, markNotificationReadApi, markAllNotificationsReadApi, fetchMe } from '../../services/api'

export default {
  data() {
    return {
      defaultAvatar: 'https://picsum.photos/200',
      myAvatar: 'https://picsum.photos/200',
      statusBarHeight: 0, // 状态栏高度
      capsuleHeight: 0,   // 胶囊高度
      topPadding: 0,       // 页面顶部预留边距

      posts: [],           // 动态列表，从API获取
      notifyCount: 0,      // 通知数量，从API获取
      showCommentModal: false,
      currentPostId: null,
      currentPostComments: [],
      newCommentText: '',
      submittingComment: false,
      showNotifyModal: false,
      notifications: [],   // 通知列表，从API获取
      loading: false,      // 加载状态
      error: null,         // 错误信息
      scrollHeight: 700    // 滚动区域高度
    }
  },
  computed: {
    // 未读数量
    unreadCount() {
      return this.notifications.filter(n => !n.read).length
    }
  },
  onLoad() {
    const cached = uni.getStorageSync('current_user')
    if (cached?.profile?.avatar) this.myAvatar = cached.profile.avatar
    this.pullMe()
    this.fetchPosts()
    if (typeof this.fetchNotifications === 'function') {
      this.fetchNotifications()
    } else {
      console.warn('fetchNotifications not ready onLoad')
    }
    this.calculateScrollHeight()

    this.setStatusBar()
    this.calculateSafeArea()
  },
  onReady() {
    this.calculateScrollHeight()
    this.setStatusBar()
  },
  onShow() {
    this.calculateScrollHeight()
    this.setStatusBar()
    // 每次显示页面时刷新数据
    this.fetchPosts()
    if (typeof this.fetchNotifications === 'function') {
      this.fetchNotifications()
    } else {
      console.warn('fetchNotifications not ready onShow')
    }
  },
  methods: {
    goToSearch() {
      uni.navigateTo({
        url: '/pages/search/search'
      })
    },
        setStatusBar() {
      try {
        const info = uni.getSystemInfoSync()
        this.statusBarHeight = info.statusBarHeight || 0
      } catch (e) {
        console.error('获取系统信息失败', e)
      }
    },

    updateUnreadCount() {
      this.notifyCount = this.notifications.filter(n => !n.read).length
    },
    async pullMe() {
      try {
        const me = await fetchMe()
        if (me?.profile?.avatar) this.myAvatar = me.profile.avatar
      } catch (e) {
        // ignore
      }
    },
    // 预取每个动态的评论数
    async prefetchCommentCounts() {
      if (!Array.isArray(this.posts) || this.posts.length === 0) return
      for (const post of this.posts) {
        try {
          const res = await getCommentsApi({ postId: post.id, page: 1, pageSize: 1 })
          const resData = res?.data || res
          const payload = resData.results || resData.data || resData
          const innerData = payload.data || payload
          const totalCount = innerData.total ?? resData.count ?? 0
          if (Number.isFinite(totalCount)) {
            post.comments = totalCount
          }
        } catch (e) {
          // 忽略单条错误，继续其他动态
        }
      }
    },
    // 获取动态列表
    async fetchPosts() {
      this.loading = true
      try {
        const response = await getPostsApi({ page: 1, pageSize: 20 })

        console.log('动态列表响应:', response)
        const rawPosts = response?.data?.results || response?.data?.posts || response?.results || []
        this.posts = (rawPosts || []).map(post => {
          const mediaArray = Array.isArray(post.media) ? post.media.filter(Boolean) : (post.media ? [post.media] : [])
          const imageRegex = /\.(png|jpe?g|webp|gif)$/i
          let type = post.type || 'image'
          let videoSrc = ''
          let images = mediaArray

          if (type === 'video') {
            videoSrc = mediaArray.find(m => m && (!imageRegex.test(m) || m.includes('/uploads/videos/'))) || mediaArray[0] || ''
            images = mediaArray.filter(m => m && m !== videoSrc && imageRegex.test(m))
          }

          return {
            id: post.id,
            name: post.user?.username || post.name,
            avatar: post.user?.profile?.avatar || post.avatar || 'https://picsum.photos/200',
            time: post.time || post.created_at,
            text: post.text,
            type,
            mediaImages: images,
            videoSrc: type === 'video' ? videoSrc : '',
            poster: '',
            tag: post.tag || '',
            tags: post.tags || [],
            likes: post.likes_count ?? post.likes ?? 0,
            comments: post.comments_count ?? post.comment_count ?? post.comments ?? (post.comments_list ? post.comments_list.length : 0),
            liked: post.is_liked ?? post.liked ?? false,
            visibility: post.visibility || 'public'
          }
        })
        // 刷新评论数（使用评论接口的 count）
        this.prefetchCommentCounts()
      } catch (error) {
        console.error('获取动态失败:', error)
        uni.showToast({ title: '获取动态失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    },
    async toggleLike(post) {
      if (!post) return
      const prevLiked = post.liked
      const prevLikes = post.likes || 0
      post.liked = !prevLiked

      post.likes = prevLiked ? Math.max(0, prevLikes - 1) : prevLikes + 1
      try {
        await likePostApi({ postId: post.id, liked: post.liked })
      } catch (e) {
        post.liked = prevLiked
        post.likes = prevLikes
        uni.showToast({ title: '点赞失败', icon: 'none' })
      }
    },
    async handleComment(item) {
      this.currentPostId = item.id
      this.showCommentModal = true
      this.fetchComments(item.id)
    },
    async fetchComments(postId) {
      try {
        const response = await getCommentsApi({ postId, page: 1, pageSize: 500 })
        console.log('获取评论响应:', response)
        // 兼容分页响应（count/next/previous/results）、包裹 success/data 的结构
        const resData = response?.data || response
        const payload = resData.results || resData.data || resData
        const innerData = payload.data || payload
        const commentsArr = innerData.comments || innerData.results || []
        if (Array.isArray(commentsArr)) {
          // ...
          this.currentPostComments = commentsArr.map(comment => ({
            id: comment.id,
            name: comment.user?.username || comment.name,
            avatar: comment.user?.profile?.avatar || comment.avatar || this.defaultAvatar,
            content: comment.content,
            time: comment.time
          }))
          // 同步评论数
          const post = this.posts.find(p => p.id === postId)
          const totalCount = innerData.total ?? resData.count ?? commentsArr.length
          if (post && Number.isFinite(totalCount)) {
            post.comments = totalCount
          }
        }
      } catch (error) {
        console.error('获取评论失败:', error)
        this.currentPostComments = []
        uni.showToast({ title: '获取评论失败', icon: 'none' })
      }
    },
    closeCommentModal() {
      this.showCommentModal = false
      this.currentPostId = null
      this.currentPostComments = []
      this.newCommentText = ''
    },
    // 提交评论
    async submitComment() {
      const content = this.newCommentText.trim()
      if (!content) {
        uni.showToast({ title: '请输入评论内容', icon: 'none' })
        return
      }

      this.submittingComment = true

      try {
        const response = await createCommentApi({ postId: this.currentPostId, content })
        if (response.success) {
          const commentData = response.data?.comment || response.data || {}
          // 更新评论列表
          const newComment = {
            id: commentData.id || Date.now(),
            name: commentData.name || '我',
            avatar: commentData.avatar || this.myAvatar || this.defaultAvatar,
            content: commentData.content || content,
            time: commentData.time || '刚刚'
          }
          this.currentPostComments.unshift(newComment)
          
          // 更新动态的评论数
          const post = this.posts.find(p => p.id === this.currentPostId)
          if (post) {
            post.comments = (post.comments || 0) + 1
          }
          
          this.newCommentText = ''
          uni.showToast({ title: '评论成功', icon: 'success' })
        }
      } catch (error) {
        console.error('提交评论失败:', error)
        uni.showToast({ title: '评论失败', icon: 'none' })
      } finally {
        this.submittingComment = false
      }
    },
    // 查看通知
    async handleNotify() {
      try {
        await this.fetchNotifications()
      } catch (e) {
        // 已在 fetchNotifications 内部记录错误
      }
      this.showNotifyModal = true
    },
    closeNotifyModal() {
      this.showNotifyModal = false
    },
    getNotifyIcon(type) {
      const icons = {
        like: '❤️',
        comment: '💬',
        follow: '➕',
        system: '🔔'
      }
      return icons[type] || '🔔'
    },

    visLabel(vis) {
      const map = {
        public: '公开',
        friends: '好友',
        private: '仅自己'
      }
      return map[vis] || '公开'
    },
    // 拉取通知列表
    async fetchNotifications() {
      try {
        const res = await getNotificationsApi()
        const data = res?.data || res || {}
        // 兼容多种返回结构：{notifications: []}、{results: []}、{data: []}
        const list = data.notifications || data.results || data.data || []
        const normalized = Array.isArray(list)
          ? list.map(n => ({
              id: n.id,
              type: n.type,
              name: n.name || n.user?.username || '系统',
              avatar: n.avatar || n.user?.profile?.avatar || this.defaultAvatar,
              time: n.time || n.created_at,
              read: n.read ?? n.is_read ?? false,
              postId: n.postId || n.post_id,
              postText: n.postText || n.post_text
            }))
          : []
        this.notifications = normalized
        this.updateUnreadCount()
      } catch (error) {
        console.error('获取通知失败:', error)
        this.notifications = []
        this.notifyCount = 0
        uni.showToast({ title: '获取通知失败', icon: 'none' })
      }
    },
    async markAllAsRead() {
      try {
        await markAllNotificationsReadApi()
        await this.fetchNotifications()
        uni.showToast({ title: '已全部标记为已读', icon: 'success' })
      } catch (error) {
        console.error('标记全部已读失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    async handleNotifyClick(notification) {
      if (!notification?.id) return
      try {
        await markNotificationReadApi(notification.id)
        // 更新本地状态，减少等待
        const target = this.notifications.find(n => n.id === notification.id)
        if (target) target.read = true
        this.updateUnreadCount()
        // 可选：关闭弹窗或跳转到帖子
        // if (notification.postId) {
        //   uni.navigateTo({ url: `/pages/post/detail?id=${notification.postId}` })
        // }
      } catch (error) {
        console.error('标记已读失败:', error)
        uni.showToast({ title: '操作失败', icon: 'none' })
      }
    },
    getNotifyText(notification) {
      const texts = {
        like: '赞了你的动态',
        comment: '评论了你的动态',
        follow: '关注了你',
        system: '系统通知'
      }
      let text = texts[notification.type] || '通知'
      if (notification.type === 'comment' && notification.commentContent) {
        text += `：${notification.commentContent}`
      }
      return text
    },

    // 状态栏与安全区
    calculateSafeArea() {
      try {
        const systemInfo = uni.getSystemInfoSync()
        const menuButtonInfo = uni.getMenuButtonBoundingClientRect ? uni.getMenuButtonBoundingClientRect() : {}
        const statusBarHeight = systemInfo.statusBarHeight || 0
        const capsuleHeight = menuButtonInfo.height || 32
        const capsuleTop = menuButtonInfo.top || statusBarHeight
        const topPadding = capsuleTop + capsuleHeight + 8
        this.statusBarHeight = statusBarHeight
        this.capsuleHeight = capsuleHeight
        this.topPadding = topPadding
      } catch (e) {
        console.error('获取胶囊信息失败', e)
        this.topPadding = 44
      }
    },
    calculateScrollHeight() {
      try {
        const systemInfo = uni.getSystemInfoSync()
        this.scrollHeight = systemInfo.windowHeight - this.topPadding - 20
        this.$nextTick(() => {
          if (this.scrollHeight <= 0) {
            this.scrollHeight = systemInfo.windowHeight - 44 - 20
          }
        })
      } catch (e) {
        console.error('计算滚动高度失败', e)
        this.scrollHeight = 600
      }
    }
  }
}
</script>

<style scoped>
.page {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: #f5f7fb;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.scroll-area {
  width: 100%;
  padding: 20rpx 24rpx;
  padding-bottom: 40rpx;
  box-sizing: border-box;
}

.search-row {
  display: flex;
  align-items: center;
  gap: 16rpx;
  width: 100%;
  box-sizing: border-box;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: #fff;
  border-radius: 999rpx;
  padding: 12rpx 18rpx;
  box-shadow: 0 10rpx 20rpx rgba(0, 0, 0, 0.04);
  border: 1rpx solid #eef0f5;
  min-width: 0;
  box-sizing: border-box;
}

.search-icon {
  margin-right: 10rpx;
  font-size: 28rpx;
}

.search-placeholder {
  flex: 1;
  font-size: 28rpx;
  color: #999;
}

.notify-btn {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  box-shadow: 0 10rpx 20rpx rgba(102, 126, 234, 0.3);
}

.badge {
  position: absolute;
  top: -6rpx;
  right: -6rpx;
  min-width: 26rpx;
  height: 26rpx;
  border-radius: 999rpx;
  background: #ff5f5f;
  color: #fff;
  font-size: 20rpx;
  padding: 0 8rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-title {
  margin: 20rpx 0;
  color: #666;
  font-size: 28rpx;
}

.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 24rpx;
  box-sizing: border-box;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.tag-wrap {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.avatar {
  width: 72rpx;
  height: 72rpx;
  border-radius: 50%;
  margin-right: 16rpx;
  background: #f2f2f2;
}

.meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.tag {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: rgba(102, 126, 234, 0.12);
  color: #667eea;
  font-size: 22rpx;
}

.visibility {
  padding: 8rpx 14rpx;
  border-radius: 12rpx;
  background: #f6f7fb;
  color: #666;
  font-size: 22rpx;
  border: 1rpx solid #eef0f5;
}

.visibility.vis-public {
  background: rgba(102, 126, 234, 0.12);
  color: #667eea;
  border-color: rgba(102, 126, 234, 0.2);
}

.visibility.vis-friends {
  background: rgba(24, 160, 88, 0.12);
  color: #18a058;
  border-color: rgba(24, 160, 88, 0.2);
}

.visibility.vis-private {
  background: rgba(153, 153, 153, 0.12);
  color: #666;
  border-color: rgba(153, 153, 153, 0.2);
}

.text {
  color: #444;
  font-size: 30rpx;
  line-height: 1.6;
  margin-bottom: 16rpx;
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

.media-video {
  width: 100%;
  box-sizing: border-box;
}

.media-video video {
  width: 100%;
  height: 360rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #000;
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

/* 消息通知弹窗 */
.notify-modal {
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

.notify-content {
  width: 100%;
  max-height: 85vh;
  background: #fff;
  border-radius: 32rpx 32rpx 0 0;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.notify-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 30rpx 32rpx;
  border-bottom: 1rpx solid #eee;
}

.notify-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
}

.notify-actions {
  display: flex;
  align-items: center;
  gap: 20rpx;
}

.mark-read-btn {
  font-size: 26rpx;
  color: #667eea;
  padding: 8rpx 16rpx;
}

.notify-list {
  flex: 1;
  padding: 20rpx 0;
  min-height: 200rpx;
  max-height: 65vh;
}

.empty-notify {
  text-align: center;
  padding: 100rpx 0;
  color: #999;
  font-size: 28rpx;
}

.notify-item {
  display: flex;
  align-items: flex-start;
  padding: 24rpx 32rpx;
  position: relative;
  background: #fff;
  transition: background 0.2s;
}

.notify-item.unread {
  background: #f8f9ff;
}

.notify-item:active {
  background: #f0f0f0;
}

.notify-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
  background: #f2f2f2;
  flex-shrink: 0;
}

.notify-body {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.notify-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8rpx;
}

.notify-name {
  font-size: 30rpx;
  color: #333;
  font-weight: 600;
}

.notify-time {
  font-size: 24rpx;
  color: #999;
}

.notify-message {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin-bottom: 8rpx;
}

.notify-icon {
  font-size: 28rpx;
}

.notify-text {
  font-size: 28rpx;
  color: #666;
  line-height: 1.5;
  flex: 1;
}

.notify-post-preview {
  margin-top: 8rpx;
  padding: 12rpx 16rpx;
  background: #f5f5f5;
  border-radius: 12rpx;
  border-left: 4rpx solid #667eea;
}

.preview-text {
  font-size: 26rpx;
  color: #888;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  overflow: hidden;
}

.unread-dot {
  position: absolute;
  top: 30rpx;
  right: 32rpx;
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
  background: #ff5f5f;
}
</style>