<template>
  <view class="page">
    <view class="logo-wrap">
      <text class="logo">Admin</text>
      <text class="sub">后台管理登录</text>
    </view>

    <view class="card">
      <text class="title">账号登录</text>
      <view class="field">
        <text class="label">用户名</text>
        <input
          class="input"
          v-model="form.username"
          placeholder="请输入管理员用户名"
          confirm-type="next"
        />
      </view>
      <view class="field">
        <text class="label">密码</text>
        <input
          class="input"
          v-model="form.password"
          placeholder="请输入密码"
          password
          confirm-type="done"
          @confirm="handleLogin"
        />
      </view>
      <button class="btn" :disabled="loading" @tap="handleLogin">
        {{ loading ? '登录中...' : '登录' }}
      </button>
      <text class="tip">使用已有登录接口，成功后进入管理控制台</text>
    </view>
  </view>
</template>

<script>
import { loginApi } from '@/services/api'

export default {
  data() {
    return {
      form: { username: '', password: '' },
      loading: false
    }
  },
  onLoad() {
    const token = uni.getStorageSync('auth_token')
    if (token) {
      uni.reLaunch({ url: '/pages/admin/console/console' })
    }
  },
  methods: {
    async handleLogin() {
      if (!this.form.username || !this.form.password) {
        uni.showToast({ title: '请输入用户名和密码', icon: 'none' })
        return
      }
      this.loading = true
      try {
        const res = await loginApi({ ...this.form })
        if (res?.token) {
          uni.setStorageSync('auth_token', res.token)
          uni.showToast({ title: '登录成功', icon: 'success' })
          setTimeout(() => {
            uni.reLaunch({ url: '/pages/admin/console/console' })
          }, 200)
        } else {
          uni.showToast({ title: res?.message || '登录失败', icon: 'none' })
        }
      } catch (e) {
        uni.showToast({ title: '登录失败', icon: 'none' })
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 32rpx;
  padding: 80rpx 40rpx;
  box-sizing: border-box;
  background: radial-gradient(circle at 20% 20%, #eff3ff, #f7f9fb 40%, #f0f4ff 70%);
}
.logo-wrap {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8rpx;
}
.logo {
  font-size: 48rpx;
  font-weight: 800;
  color: #3b5bff;
  letter-spacing: 2rpx;
}
.sub {
  font-size: 26rpx;
  color: #7b8190;
}
.card {
  width: 680rpx;
  padding: 48rpx 40rpx;
  background: #fff;
  border-radius: 28rpx;
  box-shadow: 0 24rpx 60rpx rgba(59, 91, 255, 0.12);
  display: flex;
  flex-direction: column;
  gap: 24rpx;
}
.title {
  font-size: 36rpx;
  font-weight: 700;
  color: #1f2937;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 12rpx;
}
.label {
  font-size: 26rpx;
  color: #6b7280;
}
.input {
  width: 100%;
  padding: 20rpx;
  border: 1rpx solid #e5e7eb;
  border-radius: 14rpx;
  background: #f9fafb;
  font-size: 28rpx;
}
.btn {
  width: 100%;
  padding: 24rpx;
  border-radius: 16rpx;
  background: linear-gradient(135deg, #4f80ff 0%, #6f7dec 100%);
  color: #fff;
  font-size: 30rpx;
  font-weight: 600;
}
.btn:disabled {
  opacity: 0.6;
}
.tip {
  font-size: 24rpx;
  color: #9ca3af;
  text-align: center;
}
</style>
