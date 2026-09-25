import React, { useState, useEffect } from 'react';
import { MapPin, Plus, RefreshCw, XCircle } from 'lucide-react';
import {
  getAddressesApi,
  createAddressApi,
  updateAddressApi,
  deleteAddressApi,
  setDefaultAddressApi,
} from '../../api/addresses.api';
import { AddressCard } from '../../components/checkout/AddressCard';
import { AddressForm } from '../../components/checkout/AddressForm';
import toast from 'react-hot-toast';

export default function Addresses() {
  const [addresses, setAddresses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [showModal, setShowModal] = useState(false);
  const [editingAddress, setEditingAddress] = useState(null);

  const fetchAddresses = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAddressesApi();
      setAddresses(data.results || data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load saved addresses.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAddresses();
  }, []);

  const handleCreateOrUpdate = async (formData) => {
    try {
      if (editingAddress) {
        await updateAddressApi(editingAddress.id, formData);
        toast.success('Address updated successfully!');
      } else {
        await createAddressApi(formData);
        toast.success('New address added!');
      }
      setShowModal(false);
      setEditingAddress(null);
      fetchAddresses();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to save address.');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this address?')) return;
    try {
      await deleteAddressApi(id);
      toast.success('Address deleted.');
      fetchAddresses();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to delete address.');
    }
  };

  const handleSetDefault = async (id) => {
    try {
      await setDefaultAddressApi(id);
      toast.success('Default address updated.');
      fetchAddresses();
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update default address.');
    }
  };

  const openAddModal = () => {
    setEditingAddress(null);
    setShowModal(true);
  };

  const openEditModal = (addr) => {
    setEditingAddress(addr);
    setShowModal(true);
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <h1 className="text-3xl font-bold text-white mb-8">Saved Addresses</h1>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-2xl p-6 animate-pulse space-y-3 h-48"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl">
          <p className="mb-4">{error}</p>
          <button
            onClick={fetchAddresses}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-semibold rounded-xl transition"
          >
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Saved Addresses</h1>
          <p className="text-slate-400 text-sm mt-1">Manage delivery locations for faster checkout</p>
        </div>

        <button
          onClick={openAddModal}
          className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/25"
        >
          <Plus className="w-4 h-4" /> Add New Address
        </button>
      </div>

      {addresses.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center max-w-lg mx-auto my-8">
          <div className="w-16 h-16 bg-slate-800/80 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
            <MapPin className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No Saved Addresses</h3>
          <p className="text-slate-400 text-sm mb-6">Add a delivery address to complete your orders faster.</p>
          <button
            onClick={openAddModal}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/25"
          >
            <Plus className="w-4 h-4" /> Add Address Now
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {addresses.map((addr) => (
            <AddressCard
              key={addr.id}
              address={addr}
              onEdit={openEditModal}
              onDelete={handleDelete}
              onSetDefault={handleSetDefault}
            />
          ))}
        </div>
      )}

      {/* Modal for Address Form */}
      {showModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 sm:p-8 max-w-lg w-full shadow-2xl relative">
            <h2 className="text-xl font-bold text-white mb-6">
              {editingAddress ? 'Edit Address' : 'Add New Delivery Address'}
            </h2>

            <AddressForm
              initialData={editingAddress}
              onSubmit={handleCreateOrUpdate}
              onCancel={() => {
                setShowModal(false);
                setEditingAddress(null);
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
}
