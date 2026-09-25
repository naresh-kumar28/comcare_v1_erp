import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Package, ExternalLink, RefreshCw, XCircle, CheckCircle2, Clock, Truck } from 'lucide-react';
import { getOrdersApi, cancelOrderApi } from '../../api/orders.api';
import toast from 'react-hot-toast';

const STATUS_BADGES = {
  New: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  Accepted: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
  Processing: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
  Completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
  Cancelled: 'bg-red-500/10 text-red-400 border-red-500/20',
};

export default function Orders() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingId, setCancellingId] = useState(null);
  const [filterStatus, setFilterStatus] = useState('ALL');

  const fetchOrders = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOrdersApi();
      setOrders(data.results || data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load orders. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    setCancellingId(orderId);
    try {
      await cancelOrderApi(orderId);
      toast.success('Order cancelled successfully.');
      fetchOrders();
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.error || 'Failed to cancel order.');
    } finally {
      setCancellingId(null);
    }
  };

  const filteredOrders = orders.filter((ord) => {
    if (filterStatus === 'ALL') return true;
    return ord.status?.toUpperCase() === filterStatus.toUpperCase();
  });

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <h1 className="text-3xl font-bold text-white mb-8">My Orders</h1>
        <div className="space-y-4">
          {[1, 2, 3].map((n) => (
            <div key={n} className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-pulse space-y-4">
              <div className="h-6 bg-slate-800 rounded w-1/4"></div>
              <div className="h-4 bg-slate-800 rounded w-1/2"></div>
              <div className="h-10 bg-slate-800 rounded w-1/6"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-2xl max-w-md mx-auto">
          <p className="mb-4">{error}</p>
          <button
            onClick={fetchOrders}
            className="inline-flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 text-white font-medium rounded-lg transition"
          >
            <RefreshCw className="w-4 h-4" /> Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Order History</h1>
          <p className="text-slate-400 text-sm mt-1">Track and manage your past purchases</p>
        </div>
        
        {/* Filter Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 md:pb-0 scrollbar-none">
          {['ALL', 'New', 'Processing', 'Completed', 'Cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => setFilterStatus(status)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition ${
                filterStatus === status
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/25'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:border-slate-700'
              }`}
            >
              {status === 'ALL' ? 'All Orders' : status}
            </button>
          ))}
        </div>
      </div>

      {filteredOrders.length === 0 ? (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-12 text-center max-w-lg mx-auto my-8">
          <div className="w-16 h-16 bg-slate-800/80 rounded-full flex items-center justify-center mx-auto mb-4 text-slate-400">
            <Package className="w-8 h-8" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No orders found</h3>
          <p className="text-slate-400 text-sm mb-6">
            {filterStatus === 'ALL'
              ? "You haven't placed any orders yet."
              : `No orders found with status "${filterStatus}".`}
          </p>
          <Link
            to="/products"
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition shadow-lg shadow-blue-600/25"
          >
            Start Shopping
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {filteredOrders.map((order) => {
            const statusClass = STATUS_BADGES[order.status] || 'bg-slate-800 text-slate-300 border-slate-700';
            const isCancellable = ['New', 'Accepted', 'Processing'].includes(order.status);
            const formattedDate = order.created_at
              ? new Date(order.created_at).toLocaleDateString('en-IN', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                })
              : 'N/A';

            return (
              <div
                key={order.id}
                className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition group"
              >
                {/* Header */}
                <div className="bg-slate-800/40 p-4 sm:p-6 border-b border-slate-800 flex flex-wrap items-center justify-between gap-4">
                  <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold block">Order Number</span>
                      <span className="font-mono text-sm font-bold text-white">#{order.order_number}</span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold block">Date Placed</span>
                      <span className="text-sm font-medium text-slate-300">{formattedDate}</span>
                    </div>
                    <div>
                      <span className="text-xs text-slate-500 uppercase tracking-wider font-semibold block">Total Amount</span>
                      <span className="text-sm font-bold text-emerald-400">₹{parseFloat(order.grand_total || order.total || 0).toLocaleString('en-IN')}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full border ${statusClass}`}>
                      {order.status}
                    </span>
                    {order.is_paid ? (
                      <span className="px-3 py-1 text-xs font-semibold rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/20">
                        Paid
                      </span>
                    ) : (
                      <span className="px-3 py-1 text-xs font-semibold rounded-full border bg-amber-500/10 text-amber-400 border-amber-500/20">
                        Payment Pending
                      </span>
                    )}
                  </div>
                </div>

                {/* Content Preview */}
                <div className="p-4 sm:p-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                  <div className="space-y-2 flex-1">
                    <p className="text-sm text-slate-300">
                      <span className="font-semibold text-white">{order.items?.length || 0} Item(s): </span>
                      {order.items?.map((item) => item.product_name || item.product?.name).join(', ') || 'Order details'}
                    </p>
                    {order.shipping_address && (
                      <p className="text-xs text-slate-500 flex items-center gap-1">
                        <Truck className="w-3.5 h-3.5 text-slate-400" />
                        Ship to: {typeof order.shipping_address === 'string' ? order.shipping_address : `${order.shipping_address.name}, ${order.shipping_address.city}`}
                      </p>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
                    {isCancellable && (
                      <button
                        onClick={() => handleCancelOrder(order.id)}
                        disabled={cancellingId === order.id}
                        className="px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-400 text-sm font-semibold rounded-xl border border-red-500/20 transition disabled:opacity-50"
                      >
                        {cancellingId === order.id ? 'Cancelling...' : 'Cancel Order'}
                      </button>
                    )}
                    <Link
                      to={`/orders/${order.order_number}`}
                      className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white text-sm font-semibold rounded-xl border border-slate-700 transition"
                    >
                      View Details <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
