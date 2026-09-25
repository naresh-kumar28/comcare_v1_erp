import axiosClient from './axios';

export const getProductsApi = async (params = {}) => {
  const response = await axiosClient.get('/products/', { params });
  return response.data;
};

export const getProductDetailApi = async (slug) => {
  const response = await axiosClient.get(`/products/${slug}/`);
  return response.data;
};

export const getFeaturedProductsApi = async () => {
  const response = await axiosClient.get('/products/featured/');
  return response.data;
};

export const getNewArrivalsApi = async () => {
  const response = await axiosClient.get('/products/new-arrivals/');
  return response.data;
};

export const getBestSellersApi = async () => {
  const response = await axiosClient.get('/products/best-sellers/');
  return response.data;
};
