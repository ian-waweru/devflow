import api from './axios';

export const listTasks = (params = {}) => api.get('/tasks/', { params });
export const getTask = (id) => api.get(`/tasks/${id}/`);
export const createTask = (data) => api.post('/tasks/', data);
export const updateTaskStatus = (id, statusValue) => api.patch(`/tasks/${id}/`, { status: statusValue });
export const deleteTask = (id) => api.delete(`/tasks/${id}/`);