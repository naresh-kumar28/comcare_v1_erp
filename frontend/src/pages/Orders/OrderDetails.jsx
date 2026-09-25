import React, { useEffect, useState } from 'react';
import { useParams, useSearchParams, Link, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Printer,
  Package,
  CheckCircle2,
  XCircle,
  Truck,
  CreditCard,
  MapPin,
  Clock,
  ShieldCheck,
  FileText,
} from 'lucide-react';
import { getOrderDetailApi, cancelOrderApi, getOrderInvoiceApi } from '../../api/orders.api';
import toast from 'react-hot-toast';

export default function OrderDetails() {
  const { id: orderNumber } = useParams();
  const [searchParams] = useSearchParams();
  const guestToken = searchParams.get('token');
  const navigate = useNavigate();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancelling, setCancelling] = useState(false);

  const fetchOrderDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getOrderDetailApi(orderNumber, guestToken);
      setOrder(data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load order details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderDetails();
  }, [orderNumber, guestToken]);

  const handleCancel = async () => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    setCancelling(true);
    try {
      await cancelOrderApi(order.id);
      toast.success('Order cancelled successfully.');
      fetchOrderDetails();
    } catch (err) {
      toast.error(err.response?.data?.detail || err.response?.data?.error || 'Failed to cancel order.');
    } finally {
      setCancelling(false);
    }
  };

  const handlePrintInvoice = async () => {
    try {
      const invoiceData = await getOrderInvoiceApi(orderNumber, guestToken);
      // Create printable window or trigger window.print
      window.print();
    } catch (err) {
      // Fallback to basic window.print
      window.print();
    }
  };

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-slate-800 rounded w-1/3"></div>
          <div className="h-48 bg-slate-900 rounded-2xl border border-slate-800"></div>
          <div className="h-64 bg-slate-900 rounded-2xl border border-slate-800"></div>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="max-w-md mx-auto px-4 py-16 text-center">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-xl">
          <XCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white mb-2">Order Not Found</h2>
          <p className="text-slate-400 text-sm mb-6">{error || 'Unable to locate order details.'}</p>
          <Link
            to="/orders"
            className="inline-flex items-center gap-2 px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-semibold rounded-xl transition"
          >
            <ArrowLeft className="w-4 h-4" /> Back to Orders
          </Link>
        </div>
      </div>
    );
  }

  const isCancellable = ['New', 'Accepted', 'Processing'].includes(order.status);
  const formattedDate = order.created_at
    ? new Date(order.created_at).toLocaleString('en-IN', {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : 'N/A';

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10 print:py-0 print:px-0">
      {/* Back button & Actions Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8 print:hidden">
        <button
          onClick={() => navigate(-1)}
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white transition font-medium text-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={handlePrintInvoice}
            className="inline-flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 text-sm font-semibold rounded-xl border border-slate-700 transition"
          >
            <Printer className="w-4 h-4" /> Print Invoice
          </button>

          {isCancellable && (
            <button
              onClick={handleCancel}
              disabled={cancelling}
              className="px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-400 text-sm font-semibold rounded-xl border border-red-500/20 transition disabled:opacity-50"
            >
              {cancelling ? 'Cancelling...' : 'Cancel Order'}
            </button>
          )}
        </div>
      </div>

      {/* Main Order Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl print:bg-white print:text-black print:border-none print:shadow-none">
        {/* Banner */}
        <div className="bg-gradient-to-r from-blue-900/40 via-indigo-900/20 to-slate-900 p-6 sm:p-8 border-b border-slate-800 print:bg-none print:border-b-2">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <div className="flex items-center gap-3 mb-2">
                <span className="text-xs font-bold text-blue-400 uppercase tracking-widest print:text-gray-600">Order Invoice</span>
                <span className="px-3 py-0.5 text-xs font-semibold rounded-full bg-slate-800 border border-slate-700 text-slate-300 print:border-gray-400 print:text-black">
                  {order.status}
                </span>
              </div>
              <h1 className="text-2xl sm:text-3xl font-extrabold text-white font-mono print:text-black">
                #{order.order_number}
              </h1>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1 print:text-gray-600">
                <Clock className="w-3.5 h-3.5" /> Placed on {formattedDate}
              </p>
            </div>

            <div className="text-right sm:text-right">
              <span className="text-xs text-slate-400 block mb-1 uppercase tracking-wider print:text-gray-600">Payment Status</span>
              <div className="inline-flex items-center gap-2">
                {order.is_paid ? (
                  <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 print:text-green-800">
                    <CheckCircle2 className="w-4 h-4" /> Paid
                  </span>
                ) : (
                  <span className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 print:text-amber-800">
                    <Clock className="w-4 h-4" /> Payment Pending ({order.payment_method || 'COD'})
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Details Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6 sm:p-8 border-b border-slate-800 print:border-gray-300">
          {/* Customer & Shipping */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 print:text-gray-600">
              <MapPin className="w-4 h-4 text-blue-400" /> Shipping Address
            </h3>
            {order.shipping_address ? (
              <div className="text-sm text-slate-300 space-y-1 bg-slate-800/40 p-4 rounded-xl border border-slate-800 print:bg-gray-50 print:border-gray-300 print:text-black">
                <p className="font-bold text-white print:text-black">{order.shipping_address.name || order.full_name}</p>
                <p>{order.shipping_address.street_address || order.shipping_address.address_line_1}</p>
                {order.shipping_address.address_line_2 && <p>{order.shipping_address.address_line_2}</p>}
                <p>
                  {order.shipping_address.city}, {order.shipping_address.state} - {order.shipping_address.pin_code || order.shipping_address.postal_code}
                </p>
                <p className="text-xs text-slate-400 pt-1 border-t border-slate-700/50 mt-2 print:border-gray-300">
                  Phone: {order.shipping_address.phone || order.phone}
                </p>
              </div>
            ) : (
              <p className="text-sm text-slate-500">Address info unavailable</p>
            )}
          </div>

          {/* Payment & Shipping Summary */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2 print:text-gray-600">
              <CreditCard className="w-4 h-4 text-emerald-400" /> Payment & Logistics
            </h3>
            <div className="text-sm text-slate-300 space-y-2 bg-slate-800/40 p-4 rounded-xl border border-slate-800 print:bg-gray-50 print:border-gray-300 print:text-black">
              <div className="flex justify-between py-1 border-b border-slate-700/50 print:border-gray-200">
                <span className="text-slate-400">Payment Method:</span>
                <span className="font-semibold text-white uppercase print:text-black">{order.payment_method || 'Razorpay / Online'}</span>
              </div>
              {order.razorpay_payment_id && (
                <div className="flex justify-between py-1 border-b border-slate-700/50 print:border-gray-200">
                  <span className="text-slate-400">Payment ID:</span>
                  <span className="font-mono text-xs text-slate-300">{order.razorpay_payment_id}</span>
                </div>
              )}
              {order.tracking_number && (
                <div className="flex justify-between py-1">
                  <span className="text-slate-400">Tracking Number:</span>
                  <span className="font-mono text-xs text-blue-400">{order.tracking_number}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Line Items Table */}
        <div className="p-6 sm:p-8 border-b border-slate-800 print:border-gray-300">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-4 flex items-center gap-2 print:text-gray-600">
            <Package className="w-4 h-4 text-purple-400" /> Purchased Items
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800 text-xs text-slate-400 uppercase tracking-wider print:border-gray-300 print:text-black">
                  <th className="py-3 px-2">Item</th>
                  <th className="py-3 px-2 text-right">Price</th>
                  <th className="py-3 px-2 text-center">Qty</th>
                  <th className="py-3 px-2 text-right">Total</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-sm print:divide-gray-200">
                {order.items?.map((item) => {
                  const pName = item.product_name || item.product?.name || 'Product';
                  const pPrice = parseFloat(item.price || item.unit_price || 0);
                  const itemTotal = parseFloat(item.total_price || pPrice * item.quantity);

                  return (
                    <tr key={item.id}>
                      <td className="py-4 px-2">
                        <div className="flex items-center gap-3">
                          {item.product_image && (
                            <img
                              src={item.product_image}
                              alt={pName}
                              className="w-12 h-12 object-cover rounded-lg border border-slate-800 print:hidden"
                            />
                          )}
                          <div>
                            <span className="font-semibold text-white print:text-black block">{pName}</span>
                            {item.variant_name && <span className="text-xs text-slate-400">{item.variant_name}</span>}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-2 text-right text-slate-300 print:text-black font-mono">
                        ₹{pPrice.toLocaleString('en-IN')}
                      </td>
                      <td className="py-4 px-2 text-center font-bold text-slate-200 print:text-black">
                        {item.quantity}
                      </td>
                      <td className="py-4 px-2 text-right font-mono font-bold text-white print:text-black">
                        ₹{itemTotal.toLocaleString('en-IN')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Pricing Summary */}
        <div className="p-6 sm:p-8 bg-slate-900/60 print:bg-white">
          <div className="max-w-xs sm:max-w-sm ml-auto space-y-2 text-sm">
            <div className="flex justify-between text-slate-400 print:text-gray-600">
              <span>Subtotal:</span>
              <span className="font-mono text-white print:text-black">₹{parseFloat(order.subtotal || 0).toLocaleString('en-IN')}</span>
            </div>
            {parseFloat(order.discount_amount || 0) > 0 && (
              <div className="flex justify-between text-emerald-400 font-medium">
                <span>Coupon Discount ({order.coupon_code || 'APPLIED'}):</span>
                <span className="font-mono">-₹{parseFloat(order.discount_amount).toLocaleString('en-IN')}</span>
              </div>
            )}
            <div className="flex justify-between text-slate-400 print:text-gray-600">
              <span>Shipping Charge:</span>
              <span className="font-mono text-white print:text-black">
                {parseFloat(order.shipping_charge || 0) === 0 ? 'FREE' : `₹${parseFloat(order.shipping_charge).toLocaleString('en-IN')}`}
              </span>
            </div>
            {parseFloat(order.tax_amount || 0) > 0 && (
              <div className="flex justify-between text-slate-400 print:text-gray-600">
                <span>GST Tax (18%):</span>
                <span className="font-mono text-white print:text-black">₹{parseFloat(order.tax_amount).toLocaleString('en-IN')}</span>
              </div>
            )}
            <div className="pt-3 border-t border-slate-800 flex justify-between text-base font-extrabold text-white print:border-gray-400 print:text-black">
              <span>Grand Total:</span>
              <span className="text-xl text-emerald-400 print:text-black font-mono">
                ₹{parseFloat(order.grand_total || order.total || 0).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
