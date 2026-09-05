import api from './axios';

export const listNotifications = (params = {}) => api.get('/auth/notifications/', { params });
export const markNotificationRead = (id) => api.post(`/auth/notifications/${id}/read/`);
export const markAllNotificationsRead = () => api.post('/auth/notifications/read-all/');