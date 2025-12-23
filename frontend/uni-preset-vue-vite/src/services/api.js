const BASE_URL = 'http://127.0.0.1:8000/api';

function request({ url, method = 'GET', data = {}, header = {} }) {
  return new Promise((resolve, reject) => {
    uni.request({
      url: `${BASE_URL}${url}`,
      method,
      data,
      header,
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
