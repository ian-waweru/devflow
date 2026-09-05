import api from './axios';

export const listComments = (params = {}) => api.get('/tasks/comments/', { params });
export const createComment = (data) => api.post('/tasks/comments/', data);
export const updateComment = (id, content) => api.patch(`/tasks/comments/${id}/`, { content });
export const deleteComment = (id) => api.delete(`/tasks/comments/${id}/`);