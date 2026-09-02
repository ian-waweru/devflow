import api from './axios';

export const listProjects = (params = {}) => api.get('/projects/', { params });
export const getProject = (id) => api.get(`/projects/${id}/`);
export const createProject = (data) => api.post('/projects/', data);
export const deleteProject = (id) => api.delete(`/projects/${id}/`);

export const getProjectMembers = (id) => api.get(`/projects/${id}/members/`);
export const getProjectActivity = (id) => api.get(`/projects/${id}/activity/`);
export const addProjectMember = (id, username) => api.post(`/projects/${id}/add-member/`, { username });
export const removeProjectMember = (id, username) => api.post(`/projects/${id}/remove-member/`, { username });