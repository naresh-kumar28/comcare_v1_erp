import axiosClient from './axios';

export const registerApi = async (data) => {
  const response = await axiosClient.post('/auth/register/', data);
  return response.data;
};

export const loginApi = async (credentials) => {
  const response = await axiosClient.post('/auth/login/', credentials);
  return response.data;
};

export const logoutApi = async (refreshToken) => {
  const response = await axiosClient.post('/auth/logout/', { refresh: refreshToken });
  return response.data;
};

export const getProfileApi = async () => {
  const response = await axiosClient.get('/auth/me/');
  return response.data;
};

export const updateProfileApi = async (data) => {
  const response = await axiosClient.patch('/auth/me/', data);
  return response.data;
};

export const changePasswordApi = async (data) => {
  const response = await axiosClient.post('/auth/password/change/', data);
  return response.data;
};
