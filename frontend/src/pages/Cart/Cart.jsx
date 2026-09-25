import React from 'react';
import { Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { CartLineItem } from '../../components/cart/CartLineItem';
import { CartSummary } from '../../components/cart/CartSummary';
import { ShoppingBag, ArrowLeft } from 'lucide-react';

export const Cart = () => {
  const { cart, loading } = useCart();

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center bg-white p-8 rounded-3xl border border-slate-200 text-center space-y-4 shadow-xs">
        <div className="w-20 h-20 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center">
          <ShoppingBag className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Your Shopping Cart is Empty</h2>
        <p className="text-sm text-slate-500 max-w-md">
          Looks like you haven't added any products to your cart yet. Explore our catalog to find IT equipment & laptops.
        </p>
        <Link
          to="/products"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm rounded-xl shadow-md shadow-blue-500/20 transition-all"
        >
          Start Shopping
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Shopping Cart</h1>
          <p className="text-xs text-slate-500 mt-1">{cart.total_items} items in your bag</p>
        </div>

        <Link to="/products" className="text-xs font-semibold text-blue-600 hover:underline flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Continue Shopping</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Cart Line Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.items.map((item) => (
            <CartLineItem key={item.id} item={item} />
          ))}
        </div>

        {/* Summary Sidebar */}
        <div className="lg:col-span-1">
          <CartSummary showCheckoutBtn={true} />
        </div>
      </div>
    </div>
  );
};
