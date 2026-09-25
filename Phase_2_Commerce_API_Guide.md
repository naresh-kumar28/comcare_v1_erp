# Phase 2 — Core Commerce API Guide & Flow Examples

This guide details the complete Phase 2 REST API endpoints, request/response formats, and step-by-step commerce checkout flows (both Cash on Delivery and Razorpay Online Payment).

---

## 📍 Endpoint Summary (`/api/v1/`)

### 🛒 1. Cart API (`/api/v1/cart/`)
- `GET /api/v1/cart/` - Get active cart details (supports `X-Guest-Cart-Key` header for guest users).
- `POST /api/v1/cart/items/` - Add item to cart (`product_id`, `quantity`).
- `PATCH /api/v1/cart/items/{id}/` - Update cart item quantity (`quantity`).
- `DELETE /api/v1/cart/items/{id}/` - Remove item from cart.
- `POST /api/v1/cart/merge/` - Merge guest session cart into logged-in user cart (JWT auth required).

### 🏠 2. Saved Addresses API (`/api/v1/addresses/`)
- `GET /api/v1/addresses/` - List user's or guest's saved delivery addresses.
- `POST /api/v1/addresses/` - Create a new delivery address.
- `PATCH | DELETE /api/v1/addresses/{id}/` - Update or delete an address.
- `POST /api/v1/addresses/{id}/set-default/` - Mark address as default.

### 🚚 3. Shipping Configuration API (`/api/v1/shipping-config/`)
- `GET /api/v1/shipping-config/` - Public read-only shipping rules (`flat_rate`, `free_shipping_threshold`, `is_active`).

### 🎟️ 4. Coupons API (`/api/v1/coupons/`)
- `POST /api/v1/coupons/apply/` - Validate coupon code & return calculated discount.
- `POST /api/v1/coupons/remove/` - Remove active coupon.

### 📦 5. Orders API (`/api/v1/orders/`)
- `POST /api/v1/orders/` - Place order from active cart (COD or Razorpay).
- `GET /api/v1/orders/` - List user's or guest's orders.
- `GET /api/v1/orders/{order_number}/` - Get order details.
- `POST /api/v1/orders/{id}/cancel/` - Cancel order (`pending`/`processing` status only).
- `GET /api/v1/orders/{order_number}/invoice/?token=<uuid>` - Retrieve full GST invoice JSON data.

### 💳 6. Razorpay Payments API (`/api/v1/payments/`)
- `POST /api/v1/payments/razorpay/create-order/` - Initialize gateway order for pending order.
- `POST /api/v1/payments/razorpay/verify/` - Verify client payment signature & mark order paid.
- `POST /api/v1/payments/razorpay/webhook/` - Server-to-server webhook endpoint called directly by Razorpay.

---

## 🔄 Step-by-Step E-Commerce Flow Examples

### Flow A: Guest Add-to-Cart → Apply Coupon → Place COD Order

#### Step 1: Add Item to Cart (Guest)
```http
POST /api/v1/cart/items/
X-Guest-Cart-Key: guest_session_abcd1234
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2
}
```

**Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Added Dell XPS 13 to cart.",
  "cart": {
    "cart_id": 5,
    "subtotal": "240000.00",
    "total_items": 2,
    "tax": "43200.00",
    "shipping_cost": "0.00",
    "coupon_code": null,
    "coupon_discount": "0.00",
    "grand_total": "283200.00",
    "items": [
      {
        "id": 12,
        "product_id": 1,
        "product_title": "Dell XPS 13",
        "quantity": 2,
        "unit_price": "120000.00",
        "total_price": "240000.00"
      }
    ]
  }
}
```

#### Step 2: Apply Coupon
```http
POST /api/v1/coupons/apply/
Content-Type: application/json

{
  "code": "WELCOME500",
  "cart_subtotal": 240000.00
}
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "message": "Coupon applied successfully!",
  "code": "WELCOME500",
  "discount_type": "fixed",
  "discount_value": "500.00",
  "discount_amount": "500.00"
}
```

#### Step 3: Place COD Order
```http
POST /api/v1/orders/
X-Guest-Cart-Key: guest_session_abcd1234
Content-Type: application/json

{
  "full_name": "Ramesh Kumar",
  "phone": "9876543210",
  "email": "ramesh@example.com",
  "address_line1": "Line Bazar, Near Red Cross",
  "city": "Purnea",
  "state": "Bihar",
  "pincode": "854301",
  "payment_method": "cod",
  "coupon_code": "WELCOME500"
}
```

**Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Order placed successfully.",
  "order": {
    "id": 18,
    "order_number": "BIT-ORD-48291",
    "invoice_access_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "full_name": "Ramesh Kumar",
    "phone": "9876543210",
    "email": "ramesh@example.com",
    "subtotal": "240000.00",
    "tax": "43200.00",
    "coupon_code": "WELCOME500",
    "coupon_discount": "500.00",
    "shipping_cost": "0.00",
    "grand_total": "282700.00",
    "payment_method": "cod",
    "payment_status": "pending",
    "order_status": "pending"
  }
}
```

---

### Flow B: Logged-in User → Place Order → Razorpay Online Payment → Verification

#### Step 1: Place Order with `payment_method: "razorpay"`
```http
POST /api/v1/orders/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
  "address_id": 3,
  "payment_method": "razorpay",
  "coupon_code": "WELCOME500"
}
```

**Response (`201 Created`):**
```json
{
  "success": true,
  "message": "Order created. Proceed to payment.",
  "order": {
    "order_number": "BIT-ORD-91823",
    "grand_total": "282700.00",
    "payment_method": "razorpay",
    "payment_status": "pending"
  },
  "razorpay": {
    "key_id": "rzp_test_xxxxxx",
    "amount": 28270000,
    "currency": "INR",
    "razorpay_order_id": "order_LXYZ12345"
  }
}
```

#### Step 2: Client Checkout & Signature Verification
Once Razorpay Modal completes in React frontend, send verification payload:

```http
POST /api/v1/payments/razorpay/verify/
Authorization: Bearer <jwt_access_token>
Content-Type: application/json

{
  "order_number": "BIT-ORD-91823",
  "razorpay_order_id": "order_LXYZ12345",
  "razorpay_payment_id": "pay_MQ987654",
  "razorpay_signature": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "message": "Payment verified successfully.",
  "order_number": "BIT-ORD-91823",
  "invoice_token": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

---

### 📜 3. Fetching Invoice Data (JSON for Frontend Printable Invoice)

```http
GET /api/v1/orders/BIT-ORD-91823/invoice/?token=a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

**Response (`200 OK`):**
```json
{
  "success": true,
  "invoice_number": "INV-000018",
  "invoice_date": "2026-09-25T20:15:00Z",
  "place_of_supply": "10 - Bihar",
  "customer": {
    "full_name": "Ramesh Kumar",
    "phone": "9876543210",
    "email": "ramesh@example.com",
    "address_line1": "Line Bazar, Near Red Cross",
    "city": "Purnea",
    "state": "Bihar",
    "pincode": "854301"
  },
  "items": [
    {
      "product_title": "Dell XPS 13",
      "quantity": 2,
      "unit_price": "120000.00",
      "total_price": "240000.00"
    }
  ],
  "taxable_value": "196800.00",
  "total_tax": "43200.00",
  "gst_rate": "18.0",
  "is_intra_state": true,
  "cgst_amount": "21600.00",
  "sgst_amount": "21600.00",
  "igst_amount": "0.00",
  "subtotal": "240000.00",
  "coupon_discount": "500.00",
  "shipping_cost": "0.00",
  "grand_total": "282700.00"
}
```
