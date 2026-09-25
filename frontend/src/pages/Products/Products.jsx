import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getProductsApi } from '../../api/products.api';
import { getCategoriesApi } from '../../api/categories.api';
import { ProductGrid } from '../../components/product/ProductGrid';
import { Search, Filter, SlidersHorizontal, ChevronLeft, ChevronRight, X } from 'lucide-react';

export const Products = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filter States initialized from URL search parameters
  const [search, setSearch] = useState(searchParams.get('search') || '');
  const [selectedCategory, setSelectedCategory] = useState(searchParams.get('category') || '');
  const [brand, setBrand] = useState(searchParams.get('brand') || '');
  const [minPrice, setMinPrice] = useState(searchParams.get('min_price') || '');
  const [maxPrice, setMaxPrice] = useState(searchParams.get('max_price') || '');
  const [inStock, setInStock] = useState(searchParams.get('in_stock') === 'true');
  const [ordering, setOrdering] = useState(searchParams.get('ordering') || '-created_at');
  const [page, setPage] = useState(parseInt(searchParams.get('page') || '1', 10));

  const [showFiltersMobile, setShowFiltersMobile] = useState(false);

  useEffect(() => {
    getCategoriesApi().then((data) => {
      setCategories(data.results || data || []);
    });
  }, []);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (selectedCategory) params.category = selectedCategory;
      if (brand) params.brand = brand;
      if (minPrice) params.min_price = minPrice;
      if (maxPrice) params.max_price = maxPrice;
      if (inStock) params.in_stock = true;
      if (ordering) params.ordering = ordering;
      if (page > 1) params.page = page;

      const data = await getProductsApi(params);
      setProducts(data.results || []);
      setTotalCount(data.count || 0);
      setTotalPages(data.total_pages || 1);
    } catch (err) {
      console.error('Failed to load products:', err);
      setProducts([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [searchParams]);

  const handleApplyFilters = (e) => {
    if (e) e.preventDefault();
    const newParams = {};
    if (search.trim()) newParams.search = search.trim();
    if (selectedCategory) newParams.category = selectedCategory;
    if (brand.trim()) newParams.brand = brand.trim();
    if (minPrice) newParams.min_price = minPrice;
    if (maxPrice) newParams.max_price = maxPrice;
    if (inStock) newParams.in_stock = 'true';
    if (ordering) newParams.ordering = ordering;
    newParams.page = '1';
    setPage(1);
    setSearchParams(newParams);
    setShowFiltersMobile(false);
  };

  const handleResetFilters = () => {
    setSearch('');
    setSelectedCategory('');
    setBrand('');
    setMinPrice('');
    setMaxPrice('');
    setInStock(false);
    setOrdering('-created_at');
    setPage(1);
    setSearchParams({});
  };

  const handlePageChange = (newPage) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setPage(newPage);
      const newParams = Object.fromEntries(searchParams.entries());
      newParams.page = newPage.toString();
      setSearchParams(newParams);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Catalog Store</h1>
          <p className="text-xs text-slate-500 mt-1">
            Showing {products.length} of {totalCount} products
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Search Box */}
          <form onSubmit={handleApplyFilters} className="relative flex-1 sm:w-64">
            <input
              type="text"
              placeholder="Search catalog..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            />
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          </form>

          {/* Sort Selection */}
          <select
            value={ordering}
            onChange={(e) => {
              setOrdering(e.target.value);
              const newParams = Object.fromEntries(searchParams.entries());
              newParams.ordering = e.target.value;
              setSearchParams(newParams);
            }}
            className="px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl font-medium focus:outline-none"
          >
            <option value="-created_at">Newest First</option>
            <option value="selling_price">Price: Low to High</option>
            <option value="-selling_price">Price: High to Low</option>
            <option value="-rating">Highest Rated</option>
          </select>

          {/* Mobile Filter Toggle */}
          <button
            onClick={() => setShowFiltersMobile(!showFiltersMobile)}
            className="md:hidden flex items-center space-x-1 px-3 py-2 bg-slate-100 text-slate-700 text-xs font-semibold rounded-xl"
          >
            <SlidersHorizontal className="w-4 h-4" />
            <span>Filters</span>
          </button>
        </div>
      </div>

      {/* Main Layout: Filters Sidebar + Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
        {/* Sidebar Filters */}
        <aside
          className={`md:block ${
            showFiltersMobile ? 'block fixed inset-0 z-50 bg-white p-6 overflow-y-auto' : 'hidden'
          }`}
        >
          <div className="bg-white md:bg-transparent p-4 md:p-0 rounded-2xl md:rounded-none border md:border-none border-slate-200 space-y-6">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200">
              <h3 className="font-bold text-slate-900 text-sm flex items-center space-x-2">
                <Filter className="w-4 h-4 text-blue-600" />
                <span>Filter Products</span>
              </h3>
              {showFiltersMobile && (
                <button onClick={() => setShowFiltersMobile(false)} className="text-slate-400">
                  <X className="w-5 h-5" />
                </button>
              )}
            </div>

            <form onSubmit={handleApplyFilters} className="space-y-6">
              {/* Categories */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Category</label>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.slug}>
                      {cat.name} ({cat.products_count})
                    </option>
                  ))}
                </select>
              </div>

              {/* Brand */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Brand</label>
                <input
                  type="text"
                  placeholder="e.g. Dell, Apple, HP"
                  value={brand}
                  onChange={(e) => setBrand(e.target.value)}
                  className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none"
                />
              </div>

              {/* Price Range */}
              <div>
                <label className="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">Price Range (₹)</label>
                <div className="flex items-center space-x-2">
                  <input
                    type="number"
                    placeholder="Min"
                    value={minPrice}
                    onChange={(e) => setMinPrice(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none"
                  />
                  <span className="text-slate-400 text-xs">-</span>
                  <input
                    type="number"
                    placeholder="Max"
                    value={maxPrice}
                    onChange={(e) => setMaxPrice(e.target.value)}
                    className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:outline-none"
                  />
                </div>
              </div>

              {/* Stock Filter */}
              <div className="flex items-center space-x-2 pt-1">
                <input
                  type="checkbox"
                  id="in_stock"
                  checked={inStock}
                  onChange={(e) => setInStock(e.target.checked)}
                  className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                />
                <label htmlFor="in_stock" className="text-xs font-medium text-slate-700 cursor-pointer">
                  In Stock Only
                </label>
              </div>

              {/* Filter Action Buttons */}
              <div className="pt-2 flex flex-col space-y-2">
                <button
                  type="submit"
                  className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-semibold text-xs rounded-xl transition-colors shadow-xs"
                >
                  Apply Filters
                </button>

                <button
                  type="button"
                  onClick={handleResetFilters}
                  className="w-full py-2 bg-slate-100 hover:bg-slate-200 text-slate-600 font-semibold text-xs rounded-xl transition-colors"
                >
                  Reset All
                </button>
              </div>
            </form>
          </div>
        </aside>

        {/* Product Grid Area */}
        <div className="md:col-span-3 space-y-8">
          <ProductGrid products={products} loading={loading} />

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between bg-white p-4 rounded-2xl border border-slate-200">
              <button
                onClick={() => handlePageChange(page - 1)}
                disabled={page <= 1}
                className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 rounded-xl text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
              >
                <ChevronLeft className="w-4 h-4" />
                <span>Previous</span>
              </button>

              <span className="text-xs font-medium text-slate-600">
                Page <span className="font-bold text-slate-900">{page}</span> of {totalPages}
              </span>

              <button
                onClick={() => handlePageChange(page + 1)}
                disabled={page >= totalPages}
                className="flex items-center space-x-1 px-3 py-1.5 border border-slate-200 rounded-xl text-xs font-medium text-slate-600 hover:bg-slate-50 disabled:opacity-40"
              >
                <span>Next</span>
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
