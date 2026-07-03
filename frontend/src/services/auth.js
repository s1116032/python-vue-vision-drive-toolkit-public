import apiClient from './api';

export const registerUser = (userData) => {
  return apiClient.post('/register', userData);
};

export const loginUser = (email, password) => {
  // FastAPI 的 OAuth2PasswordRequestForm 需要使用 FormData 格式
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);
  
  return apiClient.post('/login', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};