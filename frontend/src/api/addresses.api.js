import axiosClient from './axios';

export const getAddressesApi = async () => {
  const response = await axiosClient.get('/addresses/');
  return response.data;
};

export const createAddressApi = async (data) => {
  const response = await axiosClient.post('/addresses/', data);
  return response.data;
};

export const updateAddressApi = async (id, data) => {
  const response = await axiosClient.patch(`/addresses/${id}/`, data);
  return response.data;
};

export const deleteAddressApi = async (id) => {
  const response = await axiosClient.delete(`/addresses/${id}/`);
  return response.data;
};

export const setDefaultAddressApi = async (id) => {
  const response = await axiosClient.post(`/addresses/${id}/set-default/`);
  return response.data;
};
