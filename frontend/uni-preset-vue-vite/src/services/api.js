// 优先使用环境变量配置后端地址，方便切换端口/服务器；默认回落到本地 8000
const API_BASE = (import.meta.env && import.meta.env.VITE_API_BASE_URL) ? import.meta.env.VITE_API_BASE_URL : 'http://127.0.0.1:8000';
const BASE_URL = `${API_BASE}/api`;

function request({ url, method = 'GET', data = {}, header = {} }) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
      timeout: 10000, // 10 秒超时，防止长时间卡顿
      success: (res) => {
        // 2xx 视为成功
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
        } else {
          reject({ status: res.statusCode, data: res.data });
        }
      },
      fail: (err) => reject(err)
    });
  });
}

function authHeader() {
  const token = getToken();
  return token ? { Authorization: `Token ${token}` } : {};
}

export async function loginApi({ username, password }) {
  return request({
    url: '/auth/login/',
    method: 'POST',
    data: { username, password }
  });
}

export async function registerApi({ username, password, email, first_name, last_name }) {
  return request({
    url: '/users/register/',
    method: 'POST',
    data: { username, password, email, first_name, last_name }
  });
}

export async function fetchMe() {
  return request({
    url: '/setting/me/',
    method: 'GET',
    header: { ...authHeader() }
  });
}

export async function uploadAvatar(filePath) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    uni.uploadFile({
      url: `${BASE_URL}/setting/avatar/`,
      filePath,
      name: 'file',
      header: {
        ...(token ? { Authorization: `Token ${token}` } : {})
      },
      success: (res) => {
        try {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
          if (res.statusCode >= 200 && res.statusCode < 300) {
            resolve(data);
          } else {
            reject({ status: res.statusCode, data });
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => reject(err)
    });
  });
}

export async function updateMe(payload) {
  return request({
    url: '/setting/me/',
    method: 'PATCH',
    data: payload,
    header: { ...authHeader() }
  });
}

export async function changePassword({ old_password, new_password }) {
  return request({
    url: '/setting/me/password/',
    method: 'POST',
    data: { old_password, new_password },
    header: { ...authHeader() }
  });
}

// Publish APIs
export async function uploadPostImage(filePath) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    uni.uploadFile({
      url: `${BASE_URL}/publish/upload/image/`,
      filePath,
      name: 'file',
      header: {
        ...(token ? { Authorization: `Token ${token}` } : {})
      },
      success: (res) => {
        try {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
          if (res.statusCode >= 200 && res.statusCode < 300 && data?.success) {
            resolve(data.data.url);
          } else {
            reject({ status: res.statusCode, data });
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => reject(err)
    });
  });
}

export async function uploadPostVideo(filePath) {
  return new Promise((resolve, reject) => {
    const token = getToken();
    uni.uploadFile({
      url: `${BASE_URL}/publish/upload/video/`,
      filePath,
      name: 'file',
      header: {
        ...(token ? { Authorization: `Token ${token}` } : {})
      },
      success: (res) => {
        try {
          const data = typeof res.data === 'string' ? JSON.parse(res.data) : res.data;
          if (res.statusCode >= 200 && res.statusCode < 300 && data?.success) {
            resolve({ url: data.data.url, poster: data.data.poster });
          } else {
            reject({ status: res.statusCode, data });
          }
        } catch (e) {
          reject(e);
        }
      },
      fail: (err) => reject(err)
    });
  });
}

export async function createPost(payload) {
  return request({
    url: '/publish/posts/',
    method: 'POST',
    data: payload,
    header: { ...authHeader() }
  });
}

export async function fetchMyPosts() {
  return request({
    url: '/publish/posts/',
    method: 'GET',
    header: { ...authHeader() }
  });
}

export async function logoutSetting() {
  return request({
    url: '/setting/auth/logout/',
    method: 'POST',
    header: { ...authHeader() }
  });
}

// Posts API
export async function getPostsApi() {
  return request({
    url: '/posts/',
    method: 'GET'
  });
}

export async function likePostApi({ postId, liked }) {
  return request({
    url: `/posts/${postId}/like/`,
    method: 'POST',
    data: { liked },
    header: { ...authHeader() }
  });
}

export async function getCommentsApi({ postId }) {
  return request({
    url: `/posts/${postId}/comments/`,
    method: 'GET'
  });
}

export async function createCommentApi({ postId, content }) {
  return request({
    url: `/posts/${postId}/comments/`,
    method: 'POST',
    data: { content },
    header: { ...authHeader() }
  });
}

export async function deletePostApi({ postId }) {
  return request({
    url: `/posts/${postId}/delete/`,
    method: 'DELETE',
    header: { ...authHeader() }
  });
}

// Notifications API
export async function getNotificationsApi() {
  return request({
    url: '/notifications/',
    method: 'GET',
    header: { ...authHeader() }
  });
}

export async function markAsReadApi({ notificationIds = [] }) {
  return request({
    url: '/notifications/mark-as-read/',
    method: 'POST',
    data: { notificationIds },
    header: { ...authHeader() }
  });
}

export function saveToken(token) {
  uni.setStorageSync('auth_token', token);
}

export function clearToken() {
  uni.removeStorageSync('auth_token');
  uni.removeStorageSync('current_user');
}

export function getToken() {
  return uni.getStorageSync('auth_token');
}
