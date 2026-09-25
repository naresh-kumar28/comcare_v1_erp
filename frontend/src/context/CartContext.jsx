import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import {
  getCartApi,
  addToCartApi,
  updateCartItemApi,
  removeCartItemApi,
} from '../api/cart.api';
import { applyCouponApi, removeCouponApi } from '../api/coupons.api';
import toast from 'react-hot-toast';

const CartContext = createContext();

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({
    items: [],
    subtotal: '0.00',
    total_items: 0,
    tax: '0.00',
    coupon_code: null,
    coupon_discount: '0.00',
    shipping_cost: '0.00',
    grand_total: '0.00',
  });
  const [loading, setLoading] = useState(true);

  const fetchCart = useCallback(async () => {
    try {
      const data = await getCartApi();
      if (data.cart) {
        setCart(data.cart);
      }
    } catch (err) {
      console.error('Failed to fetch cart:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchCart();
  }, [fetchCart]);

  const addToCart = async (productId, quantity = 1) => {
    try {
      const data = await addToCartApi(productId, quantity);
      if (data.cart) {
        setCart(data.cart);
      }
      toast.success(data.message || 'Product added to cart!');
      return data;
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to add item to cart.';
      toast.error(msg);
      throw err;
    }
  };

  const updateQuantity = async (itemId, quantity) => {
    try {
      const data = await updateCartItemApi(itemId, quantity);
      if (data.cart) {
        setCart(data.cart);
      }
      toast.success('Cart updated.');
      return data;
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to update cart item.';
      toast.error(msg);
      throw err;
    }
  };

  const removeItem = async (itemId) => {
    try {
      const data = await removeCartItemApi(itemId);
      if (data.cart) {
        setCart(data.cart);
      }
      toast.success('Item removed from cart.');
      return data;
    } catch (err) {
      const msg = err.response?.data?.message || 'Failed to remove cart item.';
      toast.error(msg);
      throw err;
    }
  };

  const applyCoupon = async (code) => {
    try {
      const data = await applyCouponApi(code, cart.subtotal);
      toast.success(data.message || 'Coupon applied!');
      await fetchCart();
      return data;
    } catch (err) {
      const msg = err.response?.data?.message || 'Invalid or expired coupon.';
      toast.error(msg);
      throw err;
    }
  };

  const removeCoupon = async () => {
    try {
      const data = await removeCouponApi();
      toast.success('Coupon removed.');
      await fetchCart();
      return data;
    } catch (err) {
      toast.error('Failed to remove coupon.');
    }
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        loading,
        fetchCart,
        addToCart,
        updateQuantity,
        removeItem,
        applyCoupon,
        removeCoupon,
      }}
    >
      {children}
    </CartContext.Provider>
  );
};

export const useCart = () => useContext(CartContext);
