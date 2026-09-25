import React, { useState } from 'react';

export const AddressForm = ({ initialData = null, onSubmit, onCancel, loading = false }) => {
  const [formData, setFormData] = useState({
    full_name: initialData?.full_name || '',
    phone: initialData?.phone || '',
    email: initialData?.email || '',
    address_line1: initialData?.address_line1 || '',
    address_line2: initialData?.address_line2 || '',
    city: initialData?.city || 'Purnea',
    state: initialData?.state || 'Bihar',
    pincode: initialData?.pincode || '',
    address_type: initialData?.address_type || 'home',
    is_default: initialData?.is_default ?? true,
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-slate-50 p-5 rounded-2xl border border-slate-200 space-y-4">
      <h4 className="font-bold text-slate-900 text-sm">
        {initialData ? 'Edit Delivery Address' : 'Add New Delivery Address'}
      </h4>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">Full Name *</label>
          <input
            type="text"
            name="full_name"
            required
            value={formData.full_name}
            onChange={handleChange}
            className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">Phone Number *</label>
          <input
            type="tel"
            name="phone"
            required
            value={formData.phone}
            onChange={handleChange}
            className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-600 mb-1">Address Line 1 *</label>
        <input
          type="text"
          name="address_line1"
          required
          placeholder="House/Flat No., Building Name, Street"
          value={formData.address_line1}
          onChange={handleChange}
          className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-slate-600 mb-1">Address Line 2 (Optional)</label>
        <input
          type="text"
          name="address_line2"
          placeholder="Landmark, Area, Colony"
          value={formData.address_line2}
          onChange={handleChange}
          className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">City *</label>
          <input
            type="text"
            name="city"
            required
            value={formData.city}
            onChange={handleChange}
            className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">State *</label>
          <input
            type="text"
            name="state"
            required
            value={formData.state}
            onChange={handleChange}
            className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-600 mb-1">Pincode *</label>
          <input
            type="text"
            name="pincode"
            required
            maxLength={10}
            value={formData.pincode}
            onChange={handleChange}
            className="w-full px-3 py-2 text-xs bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      <div className="flex items-center justify-between pt-2">
        <div className="flex items-center space-x-4">
          <label className="flex items-center space-x-1.5 text-xs text-slate-700 cursor-pointer">
            <input
              type="radio"
              name="address_type"
              value="home"
              checked={formData.address_type === 'home'}
              onChange={handleChange}
            />
            <span>Home</span>
          </label>
          <label className="flex items-center space-x-1.5 text-xs text-slate-700 cursor-pointer">
            <input
              type="radio"
              name="address_type"
              value="work"
              checked={formData.address_type === 'work'}
              onChange={handleChange}
            />
            <span>Work</span>
          </label>
        </div>

        <label className="flex items-center space-x-2 text-xs text-slate-700 cursor-pointer">
          <input
            type="checkbox"
            name="is_default"
            checked={formData.is_default}
            onChange={handleChange}
            className="rounded border-slate-300 text-blue-600"
          />
          <span>Set as default</span>
        </label>
      </div>

      <div className="flex items-center justify-end space-x-3 pt-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-xs font-semibold text-slate-600 hover:bg-slate-200 rounded-xl"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold rounded-xl disabled:opacity-50"
        >
          {loading ? 'Saving...' : 'Save Address'}
        </button>
      </div>
    </form>
  );
};
