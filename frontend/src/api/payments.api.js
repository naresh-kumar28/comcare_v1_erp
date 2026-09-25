import axiosClient from './axios';

export const createRazorpayOrderApi = async (orderNumber) => {
  const response = await axiosClient.post('/payments/razorpay/create-order/', {
    order_number: orderNumber,
  });
  return response.data;
};

export const verifyRazorpayPaymentApi = async (data) => {
  const response = await axiosClient.post('/payments/razorpay/verify/', data);
  return response.data;
};
