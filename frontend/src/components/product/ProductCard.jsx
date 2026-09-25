import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ShoppingCart, Star, Zap } from 'lucide-react';
import { useCart } from '../../context/CartContext';

export const ProductCard = ({ product }) => {
  const { addToCart } = useCart();
  const navigate = useNavigate();

  const handleAddToCart = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product.id, 1);
  };

  const handleBuyNow = (e) => {
    e.preventDefault();
    e.stopPropagation();
    addToCart(product.id, 1).then(() => {
      navigate('/checkout');
    });
  };

  const formattedPrice = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(product.selling_price);

  const formattedOriginalPrice = product.original_price
    ? new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0,
      }).format(product.original_price)
    : null;

  return (
    <div className="group bg-white rounded-2xl border border-slate-200/80 shadow-xs hover:shadow-xl transition-all duration-300 flex flex-col overflow-hidden hover-lift">
      {/* Product Image & Badges */}
      <Link to={`/products/${product.slug}`} className="relative block aspect-[4/3] overflow-hidden bg-slate-100">
        {product.image ? (
          <img
            src={product.image}
            alt={product.title}
            className="w-full h-full object-cover object-center group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-slate-300 text-sm font-medium">
            No Image
          </div>
        )}

        {/* Badges */}
        <div className="absolute top-3 left-3 flex flex-col space-y-1.5 z-10">
          {product.is_sale && product.discount_percent && (
            <span className="bg-rose-600 text-white text-[11px] font-bold px-2.5 py-1 rounded-full shadow-xs uppercase tracking-wider">
              {product.discount_percent}% OFF
            </span>
          )}
          {product.is_featured && (
            <span className="bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-md uppercase tracking-wider">
              Featured
            </span>
          )}
        </div>

        {/* Stock Status Pill */}
        {!product.is_in_stock && (
          <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[2px] flex items-center justify-center">
            <span className="bg-rose-600 text-white font-bold text-xs px-3 py-1.5 rounded-full uppercase tracking-wider shadow-md">
              Out of Stock
            </span>
          </div>
        )}
      </Link>

      {/* Content */}
      <div className="p-4 flex-1 flex flex-col justify-between space-y-3">
        <div>
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span className="font-semibold uppercase tracking-wider text-blue-600">{product.brand || 'ComCare'}</span>
            {product.category_name && <span className="truncate">{product.category_name}</span>}
          </div>

          <Link
            to={`/products/${product.slug}`}
            className="font-semibold text-slate-900 group-hover:text-blue-600 line-clamp-2 transition-colors text-sm leading-snug"
          >
            {product.title}
          </Link>
        </div>

        {/* Rating */}
        {product.rating > 0 && (
          <div className="flex items-center space-x-1 text-xs text-amber-500 font-medium">
            <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
            <span>{product.rating}</span>
            {product.reviews_count > 0 && <span className="text-slate-400">({product.reviews_count})</span>}
          </div>
        )}

        {/* Price & Actions */}
        <div className="pt-2 border-t border-slate-100 flex items-end justify-between">
          <div>
            <div className="text-lg font-bold text-slate-900">{formattedPrice}</div>
            {formattedOriginalPrice && (
              <div className="text-xs text-slate-400 line-through font-medium">{formattedOriginalPrice}</div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleAddToCart}
              disabled={!product.is_in_stock}
              className="p-2.5 rounded-xl bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Add to Cart"
            >
              <ShoppingCart className="w-4 h-4" />
            </button>
            <button
              onClick={handleBuyNow}
              disabled={!product.is_in_stock}
              className="px-3 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-1"
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              <span>Buy</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
