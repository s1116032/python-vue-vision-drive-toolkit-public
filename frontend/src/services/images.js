import apiClient from './api';

export const uploadImages = (files) => {
  const formData = new FormData();
  for (const file of files) {
    formData.append('files', file);
  }
  
  return apiClient.post('/images/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
};

export const getImages = () => {
  return apiClient.get('/images/');
};

export const deleteImage = (id) => {
  return apiClient.delete(`/images/${id}`);
};

export const getCategories = () => {
  return apiClient.get('/images/categories');
};

export const getAnnotations = (imageId) => {
  return apiClient.get(`/images/${imageId}/annotations`);
};

export const updateAnnotations = (imageId, annotations) => {
  return apiClient.post(`/images/${imageId}/annotations`, { annotations });
};