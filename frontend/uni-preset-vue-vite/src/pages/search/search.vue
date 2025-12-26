<template>
  <view class="search-page" :style="{ paddingTop: statusBarHeight + 'px' }">
    <!-- 搜索头部 -->
    <view class="search-header">
      <view class="search-input-box">
        <text class="search-icon">🔍</text>
        <input
          class="search-input"
          type="text"
          v-model="searchForm.keyword"
          placeholder="搜索用户昵称、内容关键词"
          confirm-type="search"
          @confirm="performSearch"
          @input="onKeywordInput"
          @focus="onInputFocus"
        />
        <text class="clear-input" v-if="searchForm.keyword" @tap="clearKeyword">✕</text>
      </view>
      <text class="cancel-btn" @tap="goBack">取消</text>
    </view>

    <!-- 搜索建议（输入时显示） -->
    <view class="search-suggestions" v-if="showSuggestions && searchForm.keyword && !hasSearched">
      <view class="suggestion-item" v-for="(item, index) in suggestions" :key="index" @tap="selectSuggestion(item)">
        <text class="suggestion-icon">🔍</text>
        <text class="suggestion-text">{{ item }}</text>
      </view>
    </view>

    <!-- 搜索条件卡片 -->
    <view class="filters-card" v-if="!hasSearched">
      <view class="card-header">
        <text class="card-title">筛选条件</text>
        <text class="filter-count" v-if="hasActiveFilters">{{ activeFilterCount }} 个条件</text>
      </view>

      <!-- 标签选择 -->
      <view class="filter-group">
        <text class="filter-label">标签</text>
        <scroll-view class="tag-scroll" scroll-x>
          <view class="tag-list">
            <view
              class="tag-item"
              :class="{ active: searchForm.tag === tag }"
              v-for="tag in availableTags"
              :key="tag"
              @tap="selectTag(tag)"
            >
              {{ tag }}
            </view>
          </view>
        </scroll-view>
      </view>

      <!-- 日期选择 -->
      <view class="filter-group">
        <text class="filter-label">日期</text>
        <view class="date-container">
          <picker mode="date" :value="searchForm.date" @change="onDateChange">
            <view class="date-picker" :class="{ selected: searchForm.date }">
              <text class="date-icon">📅</text>
              <text class="date-text">{{ searchForm.date || '选择日期' }}</text>
            </view>
          </picker>
          <text class="clear-date-btn" v-if="searchForm.date" @tap="clearDate">清除</text>
        </view>
      </view>
    </view>

    <!-- 操作按钮 -->
    <view class="action-buttons" v-if="!hasSearched">
      <button class="search-action-btn primary" @tap="performSearch" :disabled="!hasActiveFilters && !searchForm.keyword.trim()">
        <text class="btn-icon">🔍</text>
        <text>搜索</text>
      </button>
      <button class="search-action-btn" @tap="resetFilters" v-if="hasActiveFilters">
        <text>重置</text>
      </button>
    </view>

    <!-- 搜索历史 -->
    <view class="history-card" v-if="!hasSearched && searchHistory.length > 0">
      <view class="card-header">
        <text class="card-title">搜索历史</text>
        <text class="clear-history-btn" @tap="clearHistory">清除全部</text>
      </view>
      <view class="history-list">
        <view
          class="history-item"
          v-for="(item, index) in searchHistory"
          :key="index"
          @tap="useHistoryItem(item)"
        >
          <view class="history-content">
            <text class="history-icon">🕐</text>
            <text class="history-text">{{ formatHistoryText(item) }}</text>
          </view>
          <text class="history-delete" @tap.stop="deleteHistoryItem(index)">✕</text>
        </view>
      </view>
    </view>

    <!-- 热门标签 -->
    <view class="hot-tags-card" v-if="!hasSearched">
      <view class="card-header">
        <text class="card-title">热门标签</text>
        <text class="card-subtitle">点击快速搜索</text>
      </view>
      <view class="hot-tags">
        <view
          class="hot-tag"
          v-for="(tag, index) in hotTags"
          :key="tag"
          :style="{ animationDelay: index * 0.1 + 's' }"
          @tap="selectHotTag(tag)"
        >
          <text class="hot-tag-icon">{{ getTagIcon(tag) }}</text>
          <text>{{ tag }}</text>
        </view>
      </view>
    </view>

    <!-- 搜索结果 -->
    <scroll-view class="results-container" scroll-y v-if="hasSearched">
      <view class="results-header">
        <view class="results-info">
          <text class="results-count">
            用户 <text class="count-number">{{ userResults.length }}</text> · 动态 <text class="count-number">{{ searchResults.length }}</text>
          </text>
          <text class="results-tip" v-if="searchForm.keyword">关键词: "{{ searchForm.keyword }}"</text>
        </view>
        <text class="clear-results-btn" @tap="clearResults">
          <text class="btn-icon">↻</text>
          <text>重新搜索</text>
        </text>
      </view>

      <!-- 用户结果 -->
      <view class="user-results">
        <view class="user-card" v-for="u in userResults" :key="u.id">
          <image class="avatar" :src="u.profile?.avatar || defaultAvatar" mode="aspectFill" />
          <view class="user-meta">
            <text class="name">{{ u.username }}</text>
            <text class="sub">ID: {{ u.id }}</text>
          </view>
          <button size="mini" class="add-btn" :disabled="adding" @tap="handleAddFriend(u)">加好友</button>
        </view>
        <view v-if="userResults.length === 0" class="empty-sub">未找到相关用户</view>
      </view>

      <!-- 动态结果 -->
      <view v-if="searchResults.length === 0" class="empty-state">
        <view class="empty-icon-wrapper">
          <text class="empty-icon">🔍</text>
        </view>
        <text class="empty-title">未找到相关内容</text>
        <text class="empty-desc">试试调整搜索条件或使用其他关键词</text>
        <button class="empty-action-btn" @tap="resetFilters">重新搜索</button>
      </view>

      <view class="results-list" v-else>
        <view 
          class="post-card" 
          v-for="(item, index) in searchResults" 
          :key="item.id"
          :style="{ animationDelay: index * 0.05 + 's' }"
        >
          <view class="post-header">
            <image class="avatar" :src="item.avatar" mode="aspectFill" />
            <view class="meta">
              <text class="name">{{ item.name }}</text>
              <text class="time">{{ item.time }}</text>
            </view>
            <text class="tag-badge" v-if="item.tag">{{ item.tag }}</text>
          </view>

          <view class="text-content" v-if="item.text">
            <rich-text :nodes="highlightKeyword(item.text)"></rich-text>
          </view>

          <view class="location-row" v-if="item.location">
            <text class="location-icon">📍</text>
            <text class="location-text">{{ item.location }}</text>
          </view>

          <view class="tags-row" v-if="item.tags && item.tags.length">
            <view class="tag" v-for="tag in item.tags" :key="tag">#{{ tag }}</view>
          </view>

          <view class="media-grid" v-if="item.type === 'image' && (item.mediaImages || item.media)">
            <image
              v-for="(img, idx) in (item.mediaImages || item.media)"
              :key="idx"
              class="media-img"
              :src="img"
              mode="aspectFill"
              @tap="previewImage(item.mediaImages || item.media, idx)"
            />
          </view>

          <view class="media-video" v-if="item.type === 'video' && (item.videoSrc || item.media)">
            <video
              class="video-player"
              :src="item.videoSrc || getMediaSrc(item.media)"
              :poster="item.poster || defaultVideoPoster"
              controls
              autoplay="false"
              show-center-play-btn
              object-fit="cover"
              playsinline
              webkit-playsinline
              x5-video-player-type="h5"
            />
          </view>
          <view class="media-grid" v-if="item.type === 'video' && item.mediaImages && item.mediaImages.length">
            <image
              v-for="(img, idx) in item.mediaImages"
              :key="idx"
              class="media-img"
              :src="img"
              mode="aspectFill"
              @tap="previewImage(item.mediaImages, idx)"
            />
          </view>

          <view class="actions-row">
            <view class="action-btn" @tap="toggleLike(item)">
              <text class="action-icon">{{ item.liked ? '❤️' : '🤍' }}</text>
              <text class="action-count">{{ item.likes }}</text>
            </view>
            <view class="action-btn" @tap="handleComment(item)">
              <text class="action-icon">💬</text>
              <text class="action-count">{{ item.comments }}</text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script>
import { searchApi, sendFriendRequestApi } from '@/services/api'
import { normalizePosts as sharedNormalizePosts } from '@/utils/postNormalize'

export default {
  data() {
    return {
      statusBarHeight: 0, // 状态栏高度
      capsuleHeight: 0,   // 胶囊高度
      topPadding: 0,      // 页面顶部预留边距
      searchForm: {
        keyword: '',
        tag: '',
        date: ''
      },
      hasSearched: false,
      isSearching: false,
      showSuggestions: false,
      searchResults: [],
      userResults: [],
      adding: false,

      searchHistory: [],
      availableTags: ['户外', '日常', '美食', '旅行', '摄影', '运动', '学习', '工作'],
      hotTags: ['户外', '美食', '旅行', '摄影', '运动', '学习'],
      suggestions: [],
      defaultAvatar: 'https://picsum.photos/200',
      defaultVideoPoster: 'https://picsum.photos/600/400'
    };
  },
  onLoad() {
    this.calculateSafeArea();
    this.setStatusBar();
    this.loadSearchHistory();

  // ...
  },
  onShow() {
    this.setStatusBar();
  },
  computed: {
    hasActiveFilters() {
      return !!(this.searchForm.tag || this.searchForm.date)
    },
    activeFilterCount() {
      let c = 0
      if (this.searchForm.tag) c += 1
      if (this.searchForm.date) c += 1
      return c
    }
  },
  methods: {
    // ...
    calculateSafeArea() {
      // 兼容旧调用，当前仅复用状态栏高度
      this.topPadding = this.statusBarHeight || 0
    },
    setStatusBar() {
      try {
        const info = uni.getSystemInfoSync();
        this.statusBarHeight = info.statusBarHeight || 0;
      } catch (e) {
        this.statusBarHeight = 0;
      }
    },
    goBack() {
      const pages = getCurrentPages()
      if (pages.length > 1) {
        uni.navigateBack()
      } else {
        // 无上级页面时直接回好友列表（替换当前页，避免堆栈）
        uni.redirectTo({ url: '/pages/friend/friend' })
      }
    },
    resetFilters() {
      this.searchForm.tag = ''
      this.searchForm.date = ''
    },
    onKeywordInput(e) {
      const keyword = e.detail.value
      if (keyword.length > 0) {
        this.showSuggestions = true
        this.generateSuggestions(keyword)
      } else {
        this.showSuggestions = false
        this.suggestions = []
      }
    },
    onInputFocus() {
      if (this.searchForm.keyword) {
        this.showSuggestions = true
      }
    },
    clearKeyword() {
      this.searchForm.keyword = ''
      this.showSuggestions = false
    },
    generateSuggestions(keyword) {
      // 简单本地提示：当前仅基于输入构造示例词（可替换为后端建议接口）
      const base = keyword.trim()
      if (!base) {
        this.suggestions = []
        return
      }
      this.suggestions = [
        base,
        `${base} 用户`,
        `${base} 标签`,
        `${base} 动态`
      ].slice(0, 5)
    },
    formatHistoryText(item) {
      if (!item) return ''
      const { keyword = '', tag = '', date = '' } = item
      const parts = []
      if (keyword) parts.push(keyword)
      if (tag) parts.push(`#${tag}`)
      if (date) parts.push(date)
      return parts.join(' · ')
    },
    selectTag(tag) {
      this.searchForm.tag = tag === this.searchForm.tag ? '' : tag
    },
    selectHotTag(tag) {
      this.searchForm.tag = tag
      this.performSearch()
    },
    useHistoryItem(item) {
      if (!item) return
      this.searchForm.keyword = item.keyword || ''
      this.searchForm.tag = item.tag || ''
      this.searchForm.date = item.date || ''
      this.performSearch()
    },
    onDateChange(e) {
      const val = e?.detail?.value || ''
      this.searchForm.date = val
    },
    clearDate() {
      this.searchForm.date = ''
    },
    clearHistory() {
      this.searchHistory = []
      this.saveSearchHistoryToStorage()
    },

    async performSearch() {

      const { keyword, tag, date } = this.searchForm

      if (this.isSearching) return
      if (!keyword.trim() && !tag && !date) {
        uni.showToast({ title: '请输入搜索条件', icon: 'none' })
        return
      }

      this.showSuggestions = false
      this.isSearching = true
      uni.showLoading({ title: '搜索中...' })

      try {
        const resp = await searchApi({
          keyword: keyword.trim(),
          tag,
          date,
          page: 1,
          pageSize: 20
        })
        if (resp && resp.success === false) {
          uni.showToast({ title: resp?.message || '搜索失败', icon: 'none' })
          return
        }
        const rawPosts = resp?.data?.results || []
        this.searchResults = this.normalizePosts(rawPosts)
        this.userResults = resp?.data?.users || []

        this.hasSearched = true
        this.saveSearchHistory({
          keyword: keyword.trim(),
          tag,
          date
        })
        uni.showToast({ 
          title: `用户${this.userResults.length} · 动态${this.searchResults.length}`, 
          icon: 'none',
          duration: 1500
        })
      } catch (e) {
        // 去掉误报，仅打印日志便于排查
        console.error('search failed', e)
      } finally {
        this.isSearching = false
        uni.hideLoading()
      }
    },

    clearResults() {
      this.hasSearched = false
      this.searchResults = []
      this.showSuggestions = false
    // ...
    },
    saveSearchHistory(record) {
      if (!record) return
      const { keyword = '', tag = '', date = '' } = record
      if (!keyword && !tag && !date) return
      const newItem = { keyword, tag, date }
      // 去重：相同 keyword/tag/date 置顶
      this.searchHistory = [
        newItem,
        ...this.searchHistory.filter(
          i => !(i.keyword === keyword && i.tag === tag && i.date === date)
        )
      ].slice(0, 20)
      this.saveSearchHistoryToStorage()
    },
    saveSearchHistoryToStorage() {
      try {
        uni.setStorageSync('searchHistory', this.searchHistory)
      } catch (e) {
        console.error('保存搜索历史失败', e)
      }
    },
    loadSearchHistory() {
      try {
        const history = uni.getStorageSync('searchHistory')
        if (history && Array.isArray(history)) {
          this.searchHistory = history
        }
      } catch (e) {
        console.error('加载搜索历史失败', e)
      }
    },

    selectSuggestion(val) {
      this.searchForm.keyword = val
      this.showSuggestions = false
      this.performSearch()
    },

    highlightKeyword(text) {
      // 保持简单返回原文本，可按需高亮关键词
      return text || ''
    },
    
    getTagIcon(tag) {
      const map = {
        美食: '🍜',
        旅行: '✈️',
        运动: '🏃',
        摄影: '📷',
        日常: '📝',
        学习: '📚',
        工作: '💼',
        户外: '⛰️',
        音乐: '🎵',
        电影: '🎬',
        读书: '📖'
      }
      return map[tag] || '🏷️'
    },

    normalizePosts(list = []) {
      return sharedNormalizePosts(list).map(p => ({
        ...p,
        name: p.name || p.user?.username || p.username || '匿名',
        avatar: p.avatar || p.user?.avatar || this.defaultAvatar,
        time: p.time || p.timesince || p.created_at || '',
        tag: p.tag || '',
        tags: Array.isArray(p.tags) ? p.tags : (p.tags ? [p.tags] : []),
        text: p.text || p.content || '',
        location: p.location || '',
        likes: p.likes_count || p.likes || 0,
        comments: p.comments_count || p.comments || 0,
        liked: p.is_liked || p.liked || false
      }))
    },

    getMediaSrc(media) {
      // 后端 video 字段可能是字符串或数组，统一取第一个
      if (Array.isArray(media)) return media[0] || ''
      return media || ''
    },

    async handleAddFriend(user) {
      if (this.adding) return
      this.adding = true
      try {
        const resp = await sendFriendRequestApi({ toUserId: user.id })
        if (resp?.success) {
          uni.showToast({ title: '申请已发送', icon: 'success' })
        } else {
          uni.showToast({ title: resp?.message || '发送失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '发送失败', icon: 'none' })
      } finally {
        this.adding = false
      }
    }
  }
}
</script>

<style scoped>
.search-page {
  width: 100%;
  min-height: 100vh;
  background: linear-gradient(180deg, #f8f9ff 0%, #f5f7fb 100%);
  box-sizing: border-box;
  overflow-x: hidden;
}

/* 搜索页面结果容器 */
.results-container {
  flex: 1;
  padding: 24rpx;
  box-sizing: border-box;
  overflow-x: hidden; /* 防止内容溢出 */
}

/* 结果列表 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

/* 结果卡片，复用发现页的 post-card 样式 */
.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 24rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  margin-bottom: 24rpx;
  box-sizing: border-box;
  animation: fadeInUp 0.5s ease backwards;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
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

.text {
  color: #444;
  font-size: 30rpx;
  line-height: 1.6;
  margin-bottom: 16rpx;
}

.location-row {
  display: flex;
  align-items: center;
  gap: 8rpx;
  margin: 6rpx 0 12rpx 0;
  color: #666;
  font-size: 26rpx;
}

.location-icon {
  font-size: 26rpx;
}

.location-text {
  color: #666;
}

.tags-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8rpx;
  margin: 6rpx 0 12rpx 0;
}

.tag {
  padding: 8rpx 14rpx;
  background: rgba(102, 126, 234, 0.12);
  color: #667eea;
  border-radius: 12rpx;
  font-size: 24rpx;
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

/* 搜索头部 */
.search-header {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 24rpx;
  background: #fff;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
  position: sticky;
  top: 0;
  z-index: 100;
  box-sizing: border-box;
}

.search-input-box {
  flex: 1;
  display: flex;
  align-items: center;
  background: #f5f7fb;
  border-radius: 999rpx;
  padding: 18rpx 24rpx;
  gap: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
  min-width: 0;
  box-sizing: border-box;
}

.search-input-box:focus-within {
  border-color: #667eea;
  background: #fff;
  box-shadow: 0 0 0 4rpx rgba(102, 126, 234, 0.1);
}

.search-icon {
  font-size: 32rpx;
  color: #999;
}

.search-input {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.clear-input {
  font-size: 24rpx;
  color: #999;
  padding: 4rpx 8rpx;
  background: #e0e0e0;
  border-radius: 50%;
  width: 32rpx;
  height: 32rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.cancel-btn {
  font-size: 28rpx;
  color: #667eea;
  font-weight: 500;
  padding: 8rpx;
}

/* 搜索建议 */
.search-suggestions {
  background: #fff;
  margin: 0 24rpx 20rpx;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
  overflow: hidden;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 20rpx 24rpx;
  border-bottom: 1rpx solid #f0f0f0;
  gap: 16rpx;
}

.suggestion-item:last-child {
  border-bottom: none;
}

.suggestion-item:active {
  background: #f5f7fb;
}

.suggestion-icon {
  font-size: 28rpx;
  color: #999;
}

.suggestion-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

/* 卡片样式 */
.filters-card,
.history-card,
.hot-tags-card {
  background: #fff;
  margin: 0 24rpx 24rpx;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 32rpx;
  color: #333;
  font-weight: 700;
}

.card-subtitle {
  font-size: 24rpx;
  color: #999;
}

.filter-count {
  font-size: 24rpx;
  color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  padding: 4rpx 12rpx;
  border-radius: 12rpx;
}

/* 筛选条件 */
.filter-group {
  margin-bottom: 32rpx;
}

.filter-group:last-child {
  margin-bottom: 0;
}

.filter-label {
  display: block;
  font-size: 28rpx;
  color: #666;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.tag-scroll {
  white-space: nowrap;
}

.tag-list {
  display: inline-flex;
  gap: 16rpx;
  padding-right: 24rpx;
}

.tag-item {
  padding: 14rpx 28rpx;
  background: #f5f7fb;
  border-radius: 999rpx;
  font-size: 26rpx;
  color: #666;
  border: 2rpx solid transparent;
  white-space: nowrap;
  transition: all 0.3s;
}

.tag-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  font-weight: 600;
  border-color: #667eea;
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
  transform: scale(1.05);
}

.date-container {
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.date-picker {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 20rpx;
  background: #f5f7fb;
  border-radius: 16rpx;
  gap: 12rpx;
  border: 2rpx solid transparent;
  transition: all 0.3s;
}

.date-picker.selected {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-color: #667eea;
}

.date-icon {
  font-size: 28rpx;
}

.date-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.clear-date-btn {
  font-size: 24rpx;
  color: #667eea;
  padding: 12rpx 20rpx;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12rpx;
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: 16rpx;
  padding: 0 24rpx 24rpx;
}

.search-action-btn {
  flex: 1;
  padding: 24rpx;
  background: #f5f7fb;
  color: #666;
  border: none;
  border-radius: 20rpx;
  font-size: 30rpx;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rpx;
}

.search-action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  box-shadow: 0 8rpx 20rpx rgba(102, 126, 234, 0.3);
}

.search-action-btn[disabled] {
  opacity: 0.5;
}

.btn-icon {
  font-size: 28rpx;
}

/* 搜索历史 */
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}

.history-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20rpx;
  background: #f5f7fb;
  border-radius: 16rpx;
  transition: all 0.3s;
}

.history-item:active {
  background: #e8eaf6;
  transform: scale(0.98);
}

.history-content {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.history-icon {
  font-size: 28rpx;
}

.history-text {
  flex: 1;
  font-size: 28rpx;
  color: #333;
}

.history-delete {
  font-size: 24rpx;
  color: #999;
  padding: 8rpx;
  background: #fff;
  border-radius: 50%;
  width: 40rpx;
  height: 40rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-history-btn {
  font-size: 26rpx;
  color: #999;
}

/* 热门标签 */
.hot-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 16rpx;
}

.hot-tag {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 18rpx 32rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-radius: 999rpx;
  font-size: 28rpx;
  color: #667eea;
  font-weight: 500;
  border: 2rpx solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s;
  animation: fadeInUp 0.5s ease backwards;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20rpx);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.hot-tag:active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-color: #667eea;
  transform: scale(1.05);
  box-shadow: 0 4rpx 12rpx rgba(102, 126, 234, 0.3);
}

.hot-tag-icon {
  font-size: 32rpx;
}

/* 搜索结果 */
.results-container {
  flex: 1;
  padding: 24rpx;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24rpx;
  padding: 20rpx;
  background: #fff;
  border-radius: 16rpx;
  box-shadow: 0 2rpx 10rpx rgba(0, 0, 0, 0.05);
}

.results-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.results-count {
  font-size: 28rpx;
  color: #666;
  font-weight: 600;
}

.count-number {
  color: #667eea;
  font-weight: 700;
  font-size: 32rpx;
}

.results-tip {
  font-size: 24rpx;
  color: #999;
}

.clear-results-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 26rpx;
  color: #667eea;
  padding: 12rpx 20rpx;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 20rpx;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 120rpx 40rpx;
  background: #fff;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.06);
}

.empty-icon-wrapper {
  width: 160rpx;
  height: 160rpx;
  margin: 0 auto 32rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-icon {
  font-size: 80rpx;
}

.empty-title {
  display: block;
  font-size: 32rpx;
  color: #333;
  font-weight: 600;
  margin-bottom: 16rpx;
}

.empty-desc {
  display: block;
  font-size: 26rpx;
  color: #999;
  margin-bottom: 40rpx;
  line-height: 1.6;
}

.empty-action-btn {
  padding: 20rpx 48rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border: none;
  border-radius: 999rpx;
  font-size: 28rpx;
  font-weight: 600;
}

/* 结果列表 */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.post-card {
  width: 100%;
  background: #fff;
  border-radius: 24rpx;
  padding: 28rpx;
  box-shadow: 0 10rpx 30rpx rgba(0, 0, 0, 0.05);
  animation: fadeInUp 0.5s ease backwards;
  box-sizing: border-box;
}

.post-header {
  display: flex;
  align-items: center;
  margin-bottom: 20rpx;
}

.avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 50%;
  margin-right: 20rpx;
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
  margin-bottom: 6rpx;
}

.time {
  font-size: 24rpx;
  color: #999;
}

.tag-badge {
  padding: 8rpx 16rpx;
  border-radius: 999rpx;
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.12) 0%, rgba(118, 75, 162, 0.12) 100%);
  color: #667eea;
  font-size: 22rpx;
  font-weight: 500;
}

.text-content {
  color: #444;
  font-size: 30rpx;
  line-height: 1.8;
  margin-bottom: 20rpx;
}

.media-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12rpx;
  margin-bottom: 20rpx;
}

.media-img {
  width: 100%;
  height: 220rpx;
  border-radius: 16rpx;
  background: #f2f2f2;
}

.media-video video {
  width: 100%;
  height: 400rpx;
  border-radius: 16rpx;
  overflow: hidden;
  background: #000;
  margin-bottom: 20rpx;
}

.actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 20rpx;
  border-top: 1rpx solid #f0f0f0;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8rpx;
  padding: 12rpx 18rpx;
  border-radius: 16rpx;
  transition: all 0.3s;
  color: #666;
  font-size: 26rpx;
}

.action-btn:active {
  background: #f5f7fb;
  transform: scale(0.96);
}

.action-icon {
  font-size: 30rpx;
}

.action-count {
  font-size: 26rpx;
  color: #666;
}
</style>