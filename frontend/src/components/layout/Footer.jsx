import React from 'react';
import { Link } from 'react-router-dom';
import { Laptop, Phone, Mail, MapPin, ShieldCheck, Truck, RefreshCw } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-300 mt-auto border-t border-slate-800">
      {/* Features Bar */}
      <div className="border-b border-slate-800 bg-slate-900/50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-3 gap-6 text-center md:text-left">
          <div className="flex items-center space-x-4 justify-center md:justify-start">
            <div className="w-12 h-12 rounded-xl bg-blue-600/10 text-blue-400 flex items-center justify-center border border-blue-500/20">
              <Truck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">Fast Dispatch & Shipping</h4>
              <p className="text-xs text-slate-400">Insured express delivery across India</p>
            </div>
          </div>

          <div className="flex items-center space-x-4 justify-center md:justify-start">
            <div className="w-12 h-12 rounded-xl bg-emerald-600/10 text-emerald-400 flex items-center justify-center border border-emerald-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">GST Compliant & Genuine</h4>
              <p className="text-xs text-slate-400">100% authentic IT products & warranty</p>
            </div>
          </div>

          <div className="flex items-center space-x-4 justify-center md:justify-start">
            <div className="w-12 h-12 rounded-xl bg-amber-600/10 text-amber-400 flex items-center justify-center border border-amber-500/20">
              <RefreshCw className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-semibold text-white text-sm">Hardware Repair Support</h4>
              <p className="text-xs text-slate-400">Expert laptop & desktop service assistance</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer Links */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold">
              <Laptop className="w-5 h-5" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">Com<span className="text-blue-500">Care</span></span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed mb-4">
            Leading supplier of laptops, desktop computers, components, and certified IT repair services in Purnea & Bihar region.
          </p>
          <div className="text-xs text-slate-400 space-y-1">
            <p className="flex items-center space-x-2"><MapPin className="w-3.5 h-3.5 text-blue-400" /> <span>Line Bazar, Purnea, Bihar 854301</span></p>
            <p className="flex items-center space-x-2"><Phone className="w-3.5 h-3.5 text-blue-400" /> <span>+91 98765 43210</span></p>
            <p className="flex items-center space-x-2"><Mail className="w-3.5 h-3.5 text-blue-400" /> <span>support@comcare.cc</span></p>
          </div>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Quick Links</h4>
          <ul className="space-y-2 text-xs">
            <li><Link to="/products" className="hover:text-blue-400 transition-colors">Catalog Store</Link></li>
            <li><Link to="/products?category=laptops" className="hover:text-blue-400 transition-colors">Laptops</Link></li>
            <li><Link to="/products?category=desktops" className="hover:text-blue-400 transition-colors">Desktop PCs</Link></li>
            <li><Link to="/cart" className="hover:text-blue-400 transition-colors">Shopping Cart</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Customer Portal</h4>
          <ul className="space-y-2 text-xs">
            <li><Link to="/orders" className="hover:text-blue-400 transition-colors">Order History</Link></li>
            <li><Link to="/addresses" className="hover:text-blue-400 transition-colors">Saved Addresses</Link></li>
            <li><Link to="/profile" className="hover:text-blue-400 transition-colors">Account Profile</Link></li>
            <li><Link to="/login" className="hover:text-blue-400 transition-colors">Sign In</Link></li>
          </ul>
        </div>

        <div>
          <h4 className="text-sm font-semibold text-white mb-4 uppercase tracking-wider">Payments & Security</h4>
          <p className="text-xs text-slate-400 mb-3">
            Supports Cash on Delivery (COD) and 256-bit SSL secured Razorpay Online Payments (UPI, Cards, NetBanking).
          </p>
          <div className="flex space-x-2 text-xs text-slate-400 font-mono">
            <span className="bg-slate-800 px-2 py-1 rounded border border-slate-700">UPI</span>
            <span className="bg-slate-800 px-2 py-1 rounded border border-slate-700">RuPay</span>
            <span className="bg-slate-800 px-2 py-1 rounded border border-slate-700">Visa</span>
            <span className="bg-slate-800 px-2 py-1 rounded border border-slate-700">Mastercard</span>
          </div>
        </div>
      </div>

      <div className="border-t border-slate-800 py-6 text-center text-xs text-slate-500">
        <p>© {new Date().getFullYear()} ComCare ERP & Store. All rights reserved.</p>
      </div>
    </footer>
  );
};
