import React from 'react';
import { ProductCard } from './ProductCard';
import { PackageX } from 'lucide-react';

export const ProductGrid = ({ products = [], loading = false, emptyMessage = 'No products found.' }) => {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <div key={i} className="bg-white rounded-2xl border border-slate-200 p-4 space-y-4 animate-pulse">
            <div className="bg-slate-200 aspect-[4/3] rounded-xl w-full"></div>
            <div className="h-4 bg-slate-200 rounded w-3/4"></div>
            <div className="h-4 bg-slate-200 rounded w-1/2"></div>
            <div className="h-8 bg-slate-200 rounded w-full pt-4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="min-h-[300px] flex flex-col items-center justify-center p-8 bg-white rounded-2xl border border-slate-200 text-center space-y-3">
        <div className="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-slate-400">
          <PackageX className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-semibold text-slate-900">{emptyMessage}</h3>
        <p className="text-sm text-slate-500 max-w-sm">
          Try clearing search keywords or changing category filters to view available inventory.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
      {products.map((product) => (
        <ProductCard key={product.id} product={product} />
      ))}
    </div>
  );
};
