import axiosClient from './axios';

export const getCategoriesApi = async () => {
  const response = await axiosClient.get('/categories/');
  return response.data;
};
