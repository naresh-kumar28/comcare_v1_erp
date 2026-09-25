import React from 'react';
import { MapPin, CheckCircle, Trash2, Edit2 } from 'lucide-react';

export const AddressCard = ({
  address,
  isSelected = false,
  onSelect,
  onEdit,
  onDelete,
  onSetDefault,
}) => {
  return (
    <div
      onClick={onSelect ? () => onSelect(address.id) : undefined}
      className={`p-4 rounded-2xl border transition-all relative ${
        onSelect ? 'cursor-pointer' : ''
      } ${
        isSelected
          ? 'border-blue-600 bg-blue-50/50 shadow-xs ring-2 ring-blue-500/20'
          : 'border-slate-200 bg-white hover:border-slate-300'
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-center space-x-2">
          <span className="bg-slate-100 text-slate-700 text-[10px] font-bold uppercase px-2 py-0.5 rounded-md border border-slate-200">
            {address.address_type || 'Home'}
          </span>
          {address.is_default && (
            <span className="bg-emerald-100 text-emerald-800 text-[10px] font-bold px-2 py-0.5 rounded-md">
              Default
            </span>
          )}
        </div>

        {isSelected && <CheckCircle className="w-5 h-5 text-blue-600" />}
      </div>

      <div className="mt-3 space-y-1">
        <h4 className="font-semibold text-slate-900 text-sm">{address.full_name}</h4>
        <p className="text-xs text-slate-600 leading-relaxed">
          {address.address_line1}, {address.address_line2 ? `${address.address_line2}, ` : ''}
          {address.city}, {address.state} - <span className="font-bold">{address.pincode}</span>
        </p>
        <p className="text-xs text-slate-500">Phone: {address.phone}</p>
      </div>

      {/* Action buttons */}
      <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
        {!address.is_default && onSetDefault && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSetDefault(address.id);
            }}
            className="text-blue-600 hover:underline font-medium"
          >
            Set as Default
          </button>
        )}

        <div className="flex items-center space-x-3 ml-auto">
          {onEdit && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onEdit(address);
              }}
              className="text-slate-500 hover:text-blue-600 flex items-center space-x-1"
            >
              <Edit2 className="w-3.5 h-3.5" />
              <span>Edit</span>
            </button>
          )}

          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(address.id);
              }}
              className="text-slate-400 hover:text-rose-600 flex items-center space-x-1"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Delete</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};
