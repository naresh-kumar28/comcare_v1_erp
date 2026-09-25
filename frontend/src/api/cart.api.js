import axiosClient from './axios';

export const getCartApi = async () => {
  const response = await axiosClient.get('/cart/');
  return response.data;
};

export const addToCartApi = async (productId, quantity = 1) => {
  const response = await axiosClient.post('/cart/items/', {
    product_id: productId,
    quantity,
  });
  return response.data;
};

export const updateCartItemApi = async (itemId, quantity) => {
  const response = await axiosClient.patch(`/cart/items/${itemId}/`, { quantity });
  return response.data;
};

export const removeCartItemApi = async (itemId) => {
  const response = await axiosClient.delete(`/cart/items/${itemId}/`);
  return response.data;
};

export const mergeCartApi = async () => {
  const response = await axiosClient.post('/cart/merge/');
  return response.data;
};
