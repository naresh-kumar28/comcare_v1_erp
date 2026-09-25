import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { getFeaturedProductsApi, getNewArrivalsApi, getBestSellersApi } from '../../api/products.api';
import { getCategoriesApi } from '../../api/categories.api';
import { ProductGrid } from '../../components/product/ProductGrid';
import { Laptop, ArrowRight, ShieldCheck, Cpu, HardDrive, Wrench } from 'lucide-react';

export const Home = () => {
  const [featuredProducts, setFeaturedProducts] = useState([]);
  const [newArrivals, setNewArrivals] = useState([]);
  const [bestSellers, setBestSellers] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [featData, newData, bestData, catData] = await Promise.all([
          getFeaturedProductsApi(),
          getNewArrivalsApi(),
          getBestSellersApi(),
          getCategoriesApi(),
        ]);

        setFeaturedProducts(featData.results || featData || []);
        setNewArrivals(newData.results || newData || []);
        setBestSellers(bestData.results || bestData || []);
        setCategories(catData.results || catData || []);
      } catch (err) {
        console.error('Failed to load home page data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="space-y-16 pb-12">
      {/* Hero Banner */}
      <section className="relative rounded-3xl bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white overflow-hidden p-8 sm:p-12 shadow-xl">
        <div className="absolute top-0 right-0 w-1/2 h-full bg-blue-600/10 blur-3xl pointer-events-none"></div>
        <div className="max-w-2xl relative z-10 space-y-6">
          <div className="inline-flex items-center space-x-2 bg-blue-500/20 border border-blue-400/30 text-blue-300 text-xs font-semibold px-3 py-1 rounded-full">
            <Cpu className="w-3.5 h-3.5" />
            <span>Authorized IT Equipment & ERP Platform</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight leading-tight">
            Premium Laptops, Desktops & Expert Repair Services
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Discover top-tier Business Laptops, Custom PC Builds, Genuine Parts & Accessories. Insured express delivery with GST billing.
          </p>

          <div className="flex flex-wrap items-center gap-4 pt-2">
            <Link
              to="/products"
              className="px-6 py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm rounded-xl shadow-lg shadow-blue-600/30 flex items-center space-x-2 transition-all hover:scale-105"
            >
              <span>Explore Catalog</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/products?category=laptops"
              className="px-6 py-3.5 bg-white/10 hover:bg-white/20 text-white font-semibold text-sm rounded-xl border border-white/15 transition-all"
            >
              Browse Laptops
            </Link>
          </div>
        </div>
      </section>

      {/* Category Quick Selector */}
      {categories.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Shop by Category</h2>
            <Link to="/products" className="text-sm font-semibold text-blue-600 hover:underline">
              View All
            </Link>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
            {categories.map((cat) => (
              <Link
                key={cat.id}
                to={`/products?category=${cat.slug}`}
                className="bg-white p-4 rounded-2xl border border-slate-200 hover:border-blue-500 hover:shadow-md transition-all text-center group flex flex-col items-center justify-center space-y-2"
              >
                <div className="w-12 h-12 rounded-xl bg-blue-50 group-hover:bg-blue-600 group-hover:text-white text-blue-600 flex items-center justify-center transition-colors">
                  <Laptop className="w-6 h-6" />
                </div>
                <span className="font-semibold text-slate-800 text-xs truncate max-w-full">
                  {cat.name}
                </span>
                <span className="text-[10px] text-slate-400 font-medium">
                  {cat.products_count} Items
                </span>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* Featured Products */}
      <section className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-slate-900 tracking-tight">Featured Collection</h2>
            <p className="text-xs text-slate-500 mt-1">Handpicked IT gear & top-rated machines</p>
          </div>
          <Link to="/products" className="text-sm font-semibold text-blue-600 hover:underline">
            View Catalog
          </Link>
        </div>

        <ProductGrid products={featuredProducts} loading={loading} />
      </section>

      {/* New Arrivals */}
      {newArrivals.length > 0 && (
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 tracking-tight">New Arrivals</h2>
              <p className="text-xs text-slate-500 mt-1">Latest specs & newly listed products</p>
            </div>
          </div>

          <ProductGrid products={newArrivals} loading={loading} />
        </section>
      )}
    </div>
  );
};
