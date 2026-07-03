import axios from 'axios';

// 建立 Axios 實例
const apiClient = axios.create({
  baseURL: '/api', // 對應 vite.config.js 中的 proxy 設定
  headers: {
    'Content-Type': 'application/json'
  }
});

// ==========================================
// Request Interceptor (請求攔截器)
// 在發送請求前，自動夾帶 JWT Token
// ==========================================
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});

// ==========================================
// Response Interceptor (回應攔截器)
// 統一處理錯誤，例如 Token 過期
// ==========================================
apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Token 無效或過期，清除本地儲存
      localStorage.removeItem('access_token');
      // 避免死循環，如果已經在登入頁就不跳轉
      if (window.location.pathname !== '/login') {
        alert('登入狀態已過期，請重新登入！');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;