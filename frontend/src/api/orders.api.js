import axiosClient from './axios';

export const placeOrderApi = async (orderData) => {
  const response = await axiosClient.post('/orders/', orderData);
  return response.data;
};

export const getOrdersApi = async () => {
  const response = await axiosClient.get('/orders/');
  return response.data;
};

export const getOrderDetailApi = async (orderNumber, token) => {
  const params = token ? { token } : {};
  const response = await axiosClient.get(`/orders/${orderNumber}/`, { params });
  return response.data;
};

export const cancelOrderApi = async (orderId) => {
  const response = await axiosClient.post(`/orders/${orderId}/cancel/`);
  return response.data;
};

export const getOrderInvoiceApi = async (orderNumber, token) => {
  const params = token ? { token } : {};
  const response = await axiosClient.get(`/orders/${orderNumber}/invoice/`, { params });
  return response.data;
};
