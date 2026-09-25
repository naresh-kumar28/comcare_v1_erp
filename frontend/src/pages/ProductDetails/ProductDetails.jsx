import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { getProductDetailApi, getProductsApi } from '../../api/products.api';
import { useCart } from '../../context/CartContext';
import { ProductGallery } from '../../components/product/ProductGallery';
import { ProductCard } from '../../components/product/ProductCard';
import { ShoppingCart, Zap, CheckCircle2, AlertCircle, Cpu, HardDrive, ShieldCheck, Star } from 'lucide-react';

export const ProductDetails = () => {
  const { slug } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();

  const [product, setProduct] = useState(null);
  const [relatedProducts, setRelatedProducts] = useState([]);
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDetail = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await getProductDetailApi(slug);
        setProduct(data);

        // Fetch related products from same category
        if (data.category?.slug) {
          const relData = await getProductsApi({ category: data.category.slug });
          const filtered = (relData.results || []).filter((p) => p.id !== data.id).slice(0, 4);
          setRelatedProducts(filtered);
        }
      } catch (err) {
        console.error('Failed to fetch product details:', err);
        setError('Product not found or has been disabled.');
      } finally {
        setLoading(false);
      }
    };

    fetchDetail();
    window.scrollTo(0, 0);
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error || !product) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4 text-center">
        <AlertCircle className="w-12 h-12 text-rose-500" />
        <h2 className="text-xl font-bold text-slate-900">{error || 'Product details unavailable.'}</h2>
        <Link to="/products" className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold">
          Back to Store Catalog
        </Link>
      </div>
    );
  }

  const handleAddToCart = () => {
    addToCart(product.id, quantity);
  };

  const handleBuyNow = () => {
    addToCart(product.id, quantity).then(() => {
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

  const specsList = [
    { label: 'Processor', value: product.processor || product.processor_short },
    { label: 'RAM', value: product.ram || product.ram_short },
    { label: 'Storage', value: product.storage || product.storage_short },
    { label: 'Graphics', value: product.graphics || product.graphics_short },
    { label: 'Display', value: product.display || product.display_short },
    { label: 'Battery', value: product.battery || product.battery_short },
    { label: 'Warranty', value: product.warranty || product.warranty_short },
  ].filter((item) => item.value);

  return (
    <div className="space-y-12">
      {/* Product Main Detail Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-10 bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-xs">
        {/* Left: Gallery */}
        <ProductGallery mainImage={product.image} galleryImages={product.gallery_images} />

        {/* Right: Info & Actions */}
        <div className="space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-blue-600 uppercase tracking-wider bg-blue-50 px-2.5 py-1 rounded-md border border-blue-100">
                {product.brand || 'ComCare'}
              </span>
              <span className="text-slate-400 font-mono">SKU: {product.sku}</span>
            </div>

            <h1 className="text-2xl sm:text-3xl font-bold text-slate-900 leading-tight">
              {product.title}
            </h1>

            {/* Rating & Stock */}
            <div className="flex items-center space-x-4 text-xs">
              {product.rating > 0 && (
                <div className="flex items-center space-x-1 text-amber-500 font-semibold bg-amber-50 px-2.5 py-1 rounded-md">
                  <Star className="w-3.5 h-3.5 fill-amber-400 text-amber-400" />
                  <span>{product.rating}</span>
                  <span>({product.reviews_count} reviews)</span>
                </div>
              )}

              {product.is_in_stock ? (
                <span className="flex items-center space-x-1 text-emerald-600 font-semibold bg-emerald-50 px-2.5 py-1 rounded-md">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>In Stock ({product.stock_qty} available)</span>
                </span>
              ) : (
                <span className="flex items-center space-x-1 text-rose-600 font-semibold bg-rose-50 px-2.5 py-1 rounded-md">
                  <AlertCircle className="w-3.5 h-3.5" />
                  <span>Out of Stock</span>
                </span>
              )}
            </div>

            {/* Price Box */}
            <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex items-baseline space-x-3">
              <span className="text-3xl font-black text-slate-900">{formattedPrice}</span>
              {formattedOriginalPrice && (
                <span className="text-sm text-slate-400 line-through font-medium">{formattedOriginalPrice}</span>
              )}
              {product.discount_percent && (
                <span className="text-xs font-bold bg-rose-600 text-white px-2 py-0.5 rounded-full uppercase">
                  Save {product.discount_percent}%
                </span>
              )}
            </div>

            {/* Short Description */}
            {product.short_description && (
              <p className="text-xs text-slate-600 leading-relaxed">{product.short_description}</p>
            )}

            {/* Technical Highlights */}
            {specsList.length > 0 && (
              <div className="space-y-2 pt-2">
                <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider">Specifications</h4>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {specsList.map((spec, i) => (
                    <div key={i} className="bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                      <span className="text-slate-400 block text-[10px] uppercase font-semibold">{spec.label}</span>
                      <span className="font-semibold text-slate-800 truncate block">{spec.value}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Quantity Stepper & Action Buttons */}
          <div className="space-y-4 pt-4 border-t border-slate-100">
            <div className="flex items-center space-x-4">
              <span className="text-xs font-semibold text-slate-600">Quantity:</span>
              <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-xl">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-8 h-8 rounded-lg bg-white flex items-center justify-center font-bold text-slate-700 shadow-xs"
                >
                  -
                </button>
                <span className="w-8 text-center text-sm font-bold">{quantity}</span>
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="w-8 h-8 rounded-lg bg-white flex items-center justify-center font-bold text-slate-700 shadow-xs"
                >
                  +
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onClick={handleAddToCart}
                disabled={!product.is_in_stock}
                className="w-full py-3.5 bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white font-bold text-sm rounded-xl flex items-center justify-center space-x-2 disabled:opacity-50 transition-all shadow-xs"
              >
                <ShoppingCart className="w-4 h-4" />
                <span>Add to Cart</span>
              </button>

              <button
                onClick={handleBuyNow}
                disabled={!product.is_in_stock}
                className="w-full py-3.5 bg-slate-900 hover:bg-blue-600 text-white font-bold text-sm rounded-xl flex items-center justify-center space-x-2 disabled:opacity-50 transition-all shadow-md"
              >
                <Zap className="w-4 h-4 text-amber-400" />
                <span>Buy Now</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Description Tab */}
      {product.description && (
        <div className="bg-white p-6 sm:p-8 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
          <h3 className="text-lg font-bold text-slate-900 border-b border-slate-100 pb-3">Product Description</h3>
          <div className="prose text-xs text-slate-600 leading-relaxed whitespace-pre-line">
            {product.description}
          </div>
        </div>
      )}

      {/* Related Products */}
      {relatedProducts.length > 0 && (
        <div className="space-y-6">
          <h3 className="text-xl font-bold text-slate-900 tracking-tight">Related Products</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6">
            {relatedProducts.map((rel) => (
              <ProductCard key={rel.id} product={rel} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
