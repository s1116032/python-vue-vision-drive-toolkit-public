import apiClient from './api';

export const createTask = (imageIds) => {
  return apiClient.post('/tasks/', { image_ids: imageIds });
};

export const getTasks = () => {
  return apiClient.get('/tasks/');
};

// 新增：下載模型 (必須設定 responseType: 'blob')
export const downloadModel = (taskId) => {
  return apiClient.get(`/tasks/${taskId}/download`, {
    responseType: 'blob'
  });
};