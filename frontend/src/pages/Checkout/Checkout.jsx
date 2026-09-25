import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useCart } from '../../context/CartContext';
import { useAuth } from '../../context/AuthContext';
import { getAddressesApi, createAddressApi, setDefaultAddressApi } from '../../api/addresses.api';
import { placeOrderApi } from '../../api/orders.api';
import { verifyRazorpayPaymentApi } from '../../api/payments.api';
import { AddressCard } from '../../components/checkout/AddressCard';
import { AddressForm } from '../../components/checkout/AddressForm';
import { CartSummary } from '../../components/cart/CartSummary';
import { CreditCard, Banknote, ShieldCheck, Plus, AlertCircle, ArrowLeft } from 'lucide-react';
import toast from 'react-hot-toast';

export const Checkout = () => {
  const { cart, fetchCart } = useCart();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [addresses, setAddresses] = useState([]);
  const [selectedAddressId, setSelectedAddressId] = useState(null);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('cod');

  const [loading, setLoading] = useState(true);
  const [placingOrder, setPlacingOrder] = useState(false);

  // Load Razorpay Script dynamically
  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';
    script.async = true;
    document.body.appendChild(script);
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  const fetchAddresses = async () => {
    try {
      const data = await getAddressesApi();
      const list = data.results || data || [];
      setAddresses(list);
      if (list.length > 0) {
        const defaultAddr = list.find((a) => a.is_default) || list[0];
        setSelectedAddressId(defaultAddr.id);
      } else {
        setShowAddressForm(true);
      }
    } catch (err) {
      console.error('Failed to load addresses:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAddresses();
  }, []);

  const handleCreateAddress = async (formData) => {
    try {
      const newAddr = await createAddressApi(formData);
      toast.success('Delivery address saved.');
      setShowAddressForm(false);
      await fetchAddresses();
      setSelectedAddressId(newAddr.id);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to save address.');
    }
  };

  const handlePlaceOrder = async () => {
    if (!selectedAddressId && !showAddressForm) {
      toast.error('Please select or add a delivery address.');
      return;
    }

    setPlacingOrder(true);

    try {
      const payload = {
        address_id: selectedAddressId,
        payment_method: paymentMethod,
        coupon_code: cart.coupon_code || '',
      };

      const res = await placeOrderApi(payload);

      if (!res.success) {
        toast.error(res.message || 'Could not place order.');
        setPlacingOrder(false);
        return;
      }

      const orderData = res.order;

      // --- Handle Razorpay Payment ---
      if (paymentMethod === 'razorpay' && res.razorpay) {
        const rzpData = res.razorpay;

        const options = {
          key: rzpData.key_id,
          amount: rzpData.amount,
          currency: rzpData.currency || 'INR',
          name: 'ComCare Store',
          description: `Order #${orderData.order_number}`,
          order_id: rzpData.razorpay_order_id,
          handler: async (response) => {
            try {
              const verifyRes = await verifyRazorpayPaymentApi({
                order_number: orderData.order_number,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              });

              if (verifyRes.success) {
                toast.success('Payment successful! Order placed.');
                await fetchCart();
                navigate(`/orders/${orderData.order_number}?token=${orderData.invoice_access_token}`);
              } else {
                toast.error('Payment verification failed.');
              }
            } catch (vErr) {
              toast.error('Payment verification error.');
            } finally {
              setPlacingOrder(false);
            }
          },
          prefill: {
            name: orderData.full_name,
            email: orderData.email || user?.email || '',
            contact: orderData.phone,
          },
          theme: {
            color: '#2563eb',
          },
          modal: {
            oncomplete: () => setPlacingOrder(false),
            ondismiss: () => {
              toast.error('Payment cancelled.');
              setPlacingOrder(false);
            },
          },
        };

        const rzp = new window.Razorpay(options);
        rzp.open();
        return;
      }

      // --- Handle Cash on Delivery (COD) ---
      toast.success('Order placed successfully via COD!');
      await fetchCart();
      navigate(`/orders/${orderData.order_number}?token=${orderData.invoice_access_token}`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to place order.');
    } finally {
      setPlacingOrder(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[50vh] flex items-center justify-center">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!cart.items || cart.items.length === 0) {
    return (
      <div className="min-h-[50vh] flex flex-col items-center justify-center space-y-4 text-center">
        <AlertCircle className="w-12 h-12 text-slate-400" />
        <h2 className="text-xl font-bold text-slate-900">Your cart is empty.</h2>
        <Link to="/products" className="px-4 py-2 bg-blue-600 text-white rounded-xl text-sm font-semibold">
          Return to Catalog
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Checkout</h1>
          <p className="text-xs text-slate-500 mt-1">Review shipping address & payment options</p>
        </div>

        <Link to="/cart" className="text-xs font-semibold text-blue-600 hover:underline flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Cart</span>
        </Link>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
        {/* Left: Address & Payment Selection */}
        <div className="lg:col-span-2 space-y-8">
          {/* Address Section */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">1. Delivery Address</h3>
              {!showAddressForm && (
                <button
                  onClick={() => setShowAddressForm(true)}
                  className="flex items-center space-x-1 text-xs font-semibold text-blue-600 hover:underline"
                >
                  <Plus className="w-4 h-4" />
                  <span>Add New Address</span>
                </button>
              )}
            </div>

            {showAddressForm ? (
              <AddressForm
                onSubmit={handleCreateAddress}
                onCancel={addresses.length > 0 ? () => setShowAddressForm(false) : null}
              />
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {addresses.map((addr) => (
                  <AddressCard
                    key={addr.id}
                    address={addr}
                    isSelected={selectedAddressId === addr.id}
                    onSelect={(id) => setSelectedAddressId(id)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Payment Method Section */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-xs space-y-4">
            <h3 className="font-bold text-slate-900 text-base border-b border-slate-100 pb-3">
              2. Select Payment Method
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* COD Option */}
              <div
                onClick={() => setPaymentMethod('cod')}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center space-x-4 ${
                  paymentMethod === 'cod'
                    ? 'border-blue-600 bg-blue-50/50 ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-700 flex items-center justify-center">
                  <Banknote className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Cash on Delivery</h4>
                  <p className="text-xs text-slate-500">Pay cash upon item delivery</p>
                </div>
              </div>

              {/* Razorpay Online Option */}
              <div
                onClick={() => setPaymentMethod('razorpay')}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex items-center space-x-4 ${
                  paymentMethod === 'razorpay'
                    ? 'border-blue-600 bg-blue-50/50 ring-2 ring-blue-500/20'
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
                  <CreditCard className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-slate-900 text-sm">Online Payment (Razorpay)</h4>
                  <p className="text-xs text-slate-500">UPI, Cards, NetBanking</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Order Summary Sidebar */}
        <div className="lg:col-span-1 space-y-4">
          <CartSummary showCheckoutBtn={false} />

          <button
            onClick={handlePlaceOrder}
            disabled={placingOrder}
            className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-bold text-base rounded-2xl shadow-lg shadow-blue-500/30 transition-all hover:scale-[1.01] disabled:opacity-50"
          >
            {placingOrder ? 'Processing Order...' : paymentMethod === 'razorpay' ? 'Proceed to Pay' : 'Confirm & Place Order'}
          </button>
        </div>
      </div>
    </div>
  );
};
