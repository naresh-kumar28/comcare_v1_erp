import axiosClient from './axios';

export const applyCouponApi = async (code, cartSubtotal) => {
  const response = await axiosClient.post('/coupons/apply/', {
    code,
    cart_subtotal: cartSubtotal,
  });
  return response.data;
};

export const removeCouponApi = async () => {
  const response = await axiosClient.post('/coupons/remove/');
  return response.data;
};
