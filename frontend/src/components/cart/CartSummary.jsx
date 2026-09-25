import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Tag, ArrowRight, ShieldCheck, Check, X } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export const CartSummary = ({ showCheckoutBtn = true }) => {
  const { cart, applyCoupon, removeCoupon } = useCart();
  const [couponInput, setCouponInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleApplyCoupon = async (e) => {
    e.preventDefault();
    if (!couponInput.trim()) return;
    setLoading(true);
    try {
      await applyCoupon(couponInput.trim());
      setCouponInput('');
    } catch (err) {
      // Error handled in context toast
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (val) =>
    new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(val || 0);

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 space-y-6 shadow-xs sticky top-24">
      <h3 className="text-lg font-bold text-slate-900 border-b border-slate-100 pb-3">Order Summary</h3>

      {/* Coupon Box */}
      <div className="space-y-2">
        <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider">Have a Coupon Code?</label>
        {cart.coupon_code ? (
          <div className="flex items-center justify-between bg-emerald-50 border border-emerald-200 px-3.5 py-2.5 rounded-xl">
            <div className="flex items-center space-x-2">
              <Check className="w-4 h-4 text-emerald-600" />
              <span className="text-sm font-bold text-emerald-700 uppercase tracking-wide">{cart.coupon_code}</span>
            </div>
            <button
              onClick={() => removeCoupon()}
              className="text-xs font-semibold text-slate-400 hover:text-rose-600 p-1"
              title="Remove Coupon"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        ) : (
          <form onSubmit={handleApplyCoupon} className="flex space-x-2">
            <div className="relative flex-1">
              <input
                type="text"
                placeholder="e.g. WELCOME500"
                value={couponInput}
                onChange={(e) => setCouponInput(e.target.value.toUpperCase())}
                className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20 uppercase font-mono"
              />
              <Tag className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-2.5" />
            </div>
            <button
              type="submit"
              disabled={loading || !couponInput.trim()}
              className="px-4 py-2 bg-slate-900 hover:bg-blue-600 text-white text-xs font-semibold rounded-xl disabled:opacity-50 transition-colors"
            >
              {loading ? '...' : 'Apply'}
            </button>
          </form>
        )}
      </div>

      {/* Breakdown List */}
      <div className="space-y-3 text-sm border-t border-slate-100 pt-4">
        <div className="flex justify-between text-slate-600">
          <span>Items Subtotal ({cart.total_items})</span>
          <span className="font-semibold text-slate-900">{formatPrice(cart.subtotal)}</span>
        </div>

        <div className="flex justify-between text-slate-600">
          <span>GST Tax (18%)</span>
          <span className="font-semibold text-slate-900">{formatPrice(cart.tax)}</span>
        </div>

        {parseFloat(cart.coupon_discount) > 0 && (
          <div className="flex justify-between text-emerald-600 font-medium">
            <span>Coupon Discount</span>
            <span>-{formatPrice(cart.coupon_discount)}</span>
          </div>
        )}

        <div className="flex justify-between text-slate-600">
          <span>Shipping Charges</span>
          <span>
            {parseFloat(cart.shipping_cost) === 0 ? (
              <span className="text-emerald-600 font-semibold uppercase text-xs">FREE</span>
            ) : (
              <span className="font-semibold text-slate-900">{formatPrice(cart.shipping_cost)}</span>
            )}
          </span>
        </div>

        <div className="border-t border-slate-200 pt-3 flex justify-between items-baseline">
          <span className="text-base font-bold text-slate-900">Grand Total</span>
          <span className="text-xl font-black text-blue-600">{formatPrice(cart.grand_total)}</span>
        </div>
      </div>

      {showCheckoutBtn && (
        <Link
          to="/checkout"
          className="w-full flex items-center justify-center space-x-2 py-3.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl shadow-md shadow-blue-500/20 transition-all hover:scale-[1.01]"
        >
          <span>Proceed to Checkout</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      )}

      <div className="flex items-center justify-center space-x-2 text-xs text-slate-400 pt-2 border-t border-slate-100">
        <ShieldCheck className="w-4 h-4 text-emerald-500" />
        <span>256-bit Encrypted SSL Checkout</span>
      </div>
    </div>
  );
};
