import React from 'react';
import { Link } from 'react-router-dom';
import { Plus, Minus, Trash2 } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export const CartLineItem = ({ item }) => {
  const { updateQuantity, removeItem } = useCart();
  const product = item.product || {};

  const handleIncrement = () => {
    updateQuantity(item.id, item.quantity + 1);
  };

  const handleDecrement = () => {
    if (item.quantity > 1) {
      updateQuantity(item.id, item.quantity - 1);
    } else {
      removeItem(item.id);
    }
  };

  const formattedUnitPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(item.unit_price);

  const formattedTotalPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(item.total_price);

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between p-4 bg-white rounded-2xl border border-slate-200 gap-4 hover:border-slate-300 transition-colors">
      {/* Product Image & Title */}
      <div className="flex items-center space-x-4 flex-1">
        <Link to={`/products/${product.slug}`} className="w-16 h-16 rounded-xl bg-slate-100 overflow-hidden flex-shrink-0 border border-slate-200">
          {product.image ? (
            <img src={product.image} alt={product.title} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-[10px] text-slate-400">No Img</div>
          )}
        </Link>
        <div>
          <Link to={`/products/${product.slug}`} className="font-semibold text-slate-900 hover:text-blue-600 text-sm line-clamp-1">
            {product.title || item.product_title}
          </Link>
          <p className="text-xs text-slate-400 font-medium mt-0.5">{formattedUnitPrice} each</p>
        </div>
      </div>

      {/* Stepper & Total & Trash */}
      <div className="flex items-center justify-between sm:justify-end w-full sm:w-auto space-x-6">
        <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl border border-slate-200">
          <button
            onClick={handleDecrement}
            className="w-7 h-7 rounded-lg bg-white flex items-center justify-center text-slate-600 hover:bg-slate-200 shadow-xs transition-colors"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
          <span className="w-8 text-center text-sm font-bold text-slate-800">{item.quantity}</span>
          <button
            onClick={handleIncrement}
            className="w-7 h-7 rounded-lg bg-white flex items-center justify-center text-slate-600 hover:bg-slate-200 shadow-xs transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="text-right font-bold text-slate-900 text-sm min-w-[90px]">
          {formattedTotalPrice}
        </div>

        <button
          onClick={() => removeItem(item.id)}
          className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
          title="Remove item"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
