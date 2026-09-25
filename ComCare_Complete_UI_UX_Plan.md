# COMCARE — Complete UI/UX Development Plan

> **Purpose:** This document is the master UI/UX specification for the ComCare React frontend.
>
> **Important:** Build the UI first with mock/static data. Do **NOT** connect DRF APIs yet. API integration will be a separate phase after the UI/UX is approved.

---

## 1. Project Context

ComCare is a franchise-based omnichannel business platform for:

- eCommerce
- Mall / physical stores
- Central Distribution
- Store Inventory
- Product-only POS billing
- Repair & Service
- Tech Mitra (Field Technician)
- AMC
- Customer Support
- Franchise management
- Reports & analytics

Current frontend setup:

```text
frontend/
├── node_modules/
├── public/
├── src/
├── .gitignore
├── eslint.config.js
├── index.html
├── package.json
├── package-lock.json
├── vite.config.js
└── README.md
```

The React + Tailwind CSS setup already exists.

---

# 2. UI/UX Development Rule

## MOST IMPORTANT RULE

Do not build the complete website in one step.

Build the frontend in controlled phases:

```text
UI-01 Design System
      ↓
UI-02 Shared Layout / Components
      ↓
UI-03 Customer eCommerce
      ↓
UI-04 Super Admin
      ↓
UI-05 Distribution
      ↓
UI-06 Franchise
      ↓
UI-07 Store Admin
      ↓
UI-08 POS
      ↓
UI-09 Support
      ↓
UI-10 Tech Mitra
      ↓
UI-11 AMC
      ↓
UI-12 Responsive + Accessibility
      ↓
UI-13 UI Polish / Final Review
      ↓
API Integration Phase
```

After each phase:

1. Implement only that phase.
2. Run the frontend.
3. Check all routes/pages.
4. Fix UI errors.
5. Verify responsive behavior.
6. Summarize changes.
7. STOP.

Never automatically start the next phase.

---

# 3. ComCare Brand Identity

The uploaded ComCare logo is the primary visual reference.

## Brand direction

The UI must feel:

- Professional
- Modern
- Premium
- Technology-focused
- Trustworthy
- Clean
- Fast
- Business-oriented

## Primary brand colors

The entire website should follow the logo's:

```text
RED
BLACK
WHITE
```

Suggested CSS variables:

```css
:root {
  --color-primary: #D4252C;
  --color-primary-hover: #D4252C;
  --color-primary-light: #FDECEC;

  --color-black: #111111;
  --color-white: #ffffff;

  --color-background: #f8f8f8;
  --color-surface: #ffffff;
  --color-surface-muted: #f3f3f3;

  --color-text: #111111;
  --color-text-muted: #666666;
  --color-border: #e5e5e5;

  --color-success: #16a34a;
  --color-warning: #f59e0b;
  --color-danger: #D4252C;
  --color-info: #2563eb;
}
```

> Exact brand red can be adjusted after comparing the final rendered UI with the supplied logo. Do not scatter hex values throughout components.

---

# 4. Centralized Theme CSS

Create one dedicated theme file:

```text
src/styles/theme.css
```

This file is the **single source of truth for website colors**.

Components should NEVER contain random hard-coded colors such as:

```jsx
className="bg-red-600"
className="text-gray-700"
```

for core brand styling.

Instead, use theme classes / CSS variables.

Example:

```css
:root {
  --brand-primary: #D4252C;
  --brand-primary-hover: #D4252C;
  --brand-primary-soft: #FDECEC;
  --brand-black: #111111;
  --brand-white: #ffffff;
}
```

Then create semantic utility classes/components around these variables.

---

# 5. One-Click Theme Switching

The architecture must make changing the complete website theme easy.

Create:

```text
src/styles/theme.css
```

and optionally:

```text
src/styles/themes.css
```

Recommended structure:

```css
:root {
  --brand-primary: #D4252C;
  --brand-primary-hover: #D4252C;
  --brand-primary-soft: #FDECEC;
  --brand-black: #111111;
  --brand-white: #ffffff;
}

[data-theme="blue"] {
  --brand-primary: #2563eb;
  --brand-primary-hover: #1d4ed8;
  --brand-primary-soft: #dbeafe;
}
```

Changing:

```html
<html data-theme="blue">
```

should change the main website color.

This means a future redesign should require editing only the theme variables rather than hundreds of components.

---

# 6. Dark Mode

Dark mode is mandatory.

Use:

```html
<html class="dark">
```

or the preferred Tailwind dark-mode strategy.

Dark mode must affect:

- Background
- Cards
- Sidebar
- Navbar
- Tables
- Forms
- Modals
- Dropdowns
- Product cards
- POS
- Charts
- Empty states
- Toasts
- Authentication pages

Recommended dark palette:

```css
.dark {
  --color-background: #0b0b0b;
  --color-surface: #151515;
  --color-surface-muted: #1e1e1e;

  --color-text: #f5f5f5;
  --color-text-muted: #a3a3a3;

  --color-border: #2b2b2b;

  --brand-primary: #D4252C;
  --brand-primary-hover: #D4252C;
}
```

Do not make every element pure black.

Use layers:

```text
#0b0b0b  → page
#151515  → card
#1e1e1e  → elevated card/input
#2b2b2b  → border
```

---

# 7. Theme Architecture

Recommended:

```text
src/
├── styles/
│   ├── theme.css
│   ├── globals.css
│   └── components.css
│
├── context/
│   └── ThemeContext.jsx
│
└── components/
    └── theme/
        └── ThemeToggle.jsx
```

Theme preferences:

- Light
- Dark
- System

Persist the user's selection using `localStorage`.

Example:

```text
comcare-theme = "dark"
```

The theme should remain after page refresh.

---

# 8. Typography

Use a modern readable font.

Recommended:

- Inter
- Manrope
- Plus Jakarta Sans

Use one primary font consistently.

Hierarchy:

```text
H1 → 32–40px
H2 → 26–32px
H3 → 20–24px
H4 → 18–20px
Body → 14–16px
Small → 12–13px
```

Avoid excessive font sizes.

---

# 9. Global Design System

Create reusable components:

```text
Button
Input
Select
Textarea
Checkbox
Radio
Switch
Badge
Avatar
Card
Modal
Drawer
Dropdown
Tabs
Table
Pagination
Breadcrumb
Tooltip
Toast
Alert
Skeleton
EmptyState
LoadingState
ConfirmDialog
SearchBox
DatePicker
StatusBadge
StatCard
```

Every panel must reuse these components.

---

# 10. Border Radius

Use a consistent radius system.

```text
sm   → 6px
md   → 8px
lg   → 12px
xl   → 16px
2xl  → 20px
```

Do not mix many unrelated border-radius values.

---

# 11. Shadows

Use subtle shadows in light mode.

Example:

```text
Card:
shadow-sm

Important modal:
shadow-xl
```

Dark mode should use borders and surface contrast more than heavy shadows.

---

# 12. Layout System

Dashboard layout:

```text
┌─────────────────────────────────────────────┐
│ Top Navbar                                  │
├───────────────┬─────────────────────────────┤
│               │                             │
│ Sidebar       │ Main Content                │
│               │                             │
│               │                             │
└───────────────┴─────────────────────────────┘
```

Desktop:

- Sidebar: 250–280px
- Main content: flexible

Tablet:

- Collapsible sidebar

Mobile:

- Sidebar becomes drawer
- Bottom/quick actions where appropriate

---

# 13. Global Navbar

Include:

- ComCare logo
- Search
- Notifications
- Theme toggle
- User profile
- Role indicator
- Mobile menu

For customer website:

```text
Logo
Categories
Search
Wishlist
Cart
Account
```

For dashboards:

```text
Logo
Global Search
Notifications
Theme
Profile
```

---

# 14. Sidebar

Sidebar should be role-aware.

Do not show every menu item to every role.

Example:

### Super Admin

```text
Dashboard
Franchises
Stores
Products
Inventory
Distribution
Orders
Services
Tech Mitra
AMC
Support
Returns
Reports
Settings
```

### Distribution

```text
Dashboard
Purchase Requests
Central Inventory
Suppliers
Distribution Orders
Dispatch
Goods Receipt
Stock Transfer
Reports
```

### Franchise

```text
Dashboard
My Franchise
Stores
Purchase Requests
Inventory
Sales
Services
Tech Mitra
Finance
Reports
```

### Store Admin

```text
Dashboard
POS
Inventory
Purchase Requests
Sales
Customers
Services
Returns
Staff
Reports
```

### Tech Mitra

```text
Dashboard
My Jobs
Calendar
Customers
Service History
Earnings
Profile
```

---

# 15. UI-01 — Design System Phase

Build first:

- Theme CSS
- Dark mode
- Theme toggle
- Typography
- Buttons
- Inputs
- Cards
- Tables
- Badges
- Modals
- Toasts
- Sidebar
- Navbar
- Responsive layout
- Loading states
- Empty states

Use mock examples.

Do NOT build business pages yet.

---

# 16. UI-02 — Shared Dashboard Layout

Create reusable:

```text
DashboardLayout
Sidebar
TopNavbar
PageHeader
Breadcrumb
StatCard
DataTable
FilterBar
ActionMenu
```

Example:

```text
DashboardLayout
├── Sidebar
├── Navbar
└── Main
    ├── Breadcrumb
    ├── PageHeader
    └── PageContent
```

---

# 17. UI-03 — Customer eCommerce 

## Pages

```text
/
 /shop
 /categories
 /category/:slug
 /product/:slug
 /wishlist
 /cart
 /checkout
 /payment
 /order-success
 /orders
 /orders/:id
 /track-order
 /returns
 /services
 /services/book
 /amc
 /profile
 /addresses
 /support
 /login
 /register
```

## Home page

Sections:

1. Announcement bar
2. Navbar
3. Hero
4. Categories
5. Featured products
6. Deals
7. Services
8. AMC
9. Why ComCare
10. Franchise CTA
11. Customer reviews
12. Footer

Use red strategically.

Do not make the entire page red.

---

# 18. Product Listing UI

Include:

- Search
- Category
- Brand
- Price
- Rating
- Availability
- Sort
- Grid/list toggle

Product card:

```text
Image
Wishlist
Badge
Brand
Product name
Rating
Price
Discount
Add to Cart
Buy Now
```

---

# 19. Product Details UI

Include:

- Image gallery
- Product title
- Rating
- SKU
- Price
- Discount
- Stock
- Product highlights
- Specifications
- Description
- Warranty
- AMC option
- Delivery information
- Add to cart
- Buy now
- Related products
- Reviews

---

# 20. Cart

```text
Product
Quantity
Price
Discount
Subtotal
Remove
Save for later
```

Order summary:

```text
Subtotal
Discount
Shipping
Tax
Grand Total
Checkout
```

---

# 21. Checkout

Steps:

```text
Address
  ↓
Delivery
  ↓
Payment
  ↓
Confirmation
```

Use a clean stepper.

---

# 22. Customer Account Dashboard

Cards:

```text
Orders
Wishlist
Returns
Services
AMC
Support
```

Include:

- Profile
- Addresses
- Recent orders
- Active services
- Active AMC
- Support tickets

---

# 23. UI-04 — Super Admin

Route:

```text
/admin
```

## Dashboard

Top stats:

```text
Total Revenue
Total Orders
Franchises
Stores
Customers
Products
Service Requests
Pending Tickets
```

Sections:

- Revenue chart
- Sales chart
- Franchise performance
- Store performance
- Recent orders
- Pending purchase requests
- Service activity
- Low-stock alerts

---

# 24. Super Admin Pages

```text
/admin/franchises
/admin/franchises/:id
/admin/stores
/admin/products
/admin/categories
/admin/brands
/admin/inventory
/admin/distribution
/admin/orders
/admin/services
/admin/technicians
/admin/amc
/admin/support
/admin/returns
/admin/reports
/admin/settings
```

---

# 25. Franchise Management UI

List:

```text
Franchise ID
Name
Owner
Location
Stores
Status
Revenue
Created
Actions
```

Details page:

```text
Overview
Stores
Sales
Inventory
Purchase Requests
Services
Finance
Documents
Agreement
```

---

# 26. Store Management UI

Store list:

```text
Store
Franchise
Manager
Location
Inventory
Today's Sales
Status
```

Store details:

```text
Overview
Inventory
POS Sales
Staff
Services
Purchase Requests
Reports
```

---

# 27. UI-05 — Distribution Panel

Route:

```text
/distribution
```

Dashboard stats:

```text
Pending Requests
Approved Requests
Dispatched
In Transit
Received
Low Stock
```

Pages:

```text
/distribution/requests
/distribution/requests/:id
/distribution/inventory
/distribution/suppliers
/distribution/orders
/distribution/dispatch
/distribution/goods-receipt
/distribution/stock-transfer
/distribution/reports
```

---

# 28. Distribution Purchase Request UI

Request details:

```text
Request ID
Franchise
Store
Requested By
Date
Priority
Items
Quantity
Current Store Stock
Status
```

Actions:

```text
Approve
Reject
Edit Quantity
Add Note
Create Distribution Order
```

---

# 29. Distribution Order UI

Workflow visualization:

```text
Requested
   ↓
Approved
   ↓
Processing
   ↓
Packed
   ↓
Dispatched
   ↓
In Transit
   ↓
Received
```

Show a timeline.

---

# 30. UI-06 — Franchise Dashboard

Route:

```text
/franchise
```

Stats:

```text
Total Stores
Today's Sales
Monthly Revenue
Current Stock
Pending Requests
Service Requests
```

Pages:

```text
/franchise/profile
/franchise/stores
/franchise/purchase-requests
/franchise/inventory
/franchise/sales
/franchise/services
/franchise/technicians
/franchise/finance
/franchise/reports
```

---

# 31. Franchise Purchase Request UI

Store/Franchise can request stock from Central Distribution.

Flow:

```text
Select Store
   ↓
Search Product
   ↓
Add Quantity
   ↓
Add Note
   ↓
Submit Request
```

Request tracking:

```text
Submitted
Under Review
Approved
Packed
Dispatched
Received
```

---

# 32. UI-07 — Store Admin

Route:

```text
/store
```

Dashboard:

```text
Today's Sales
Today's Orders
Current Stock
Low Stock
Pending Services
Pending Returns
```

Pages:

```text
/store/inventory
/store/purchase-requests
/store/sales
/store/customers
/store/services
/store/returns
/store/staff
/store/reports
```

---

# 33. UI-08 — POS

## IMPORTANT

POS is ONLY for product billing.

Do not mix service billing into this interface.

Route:

```text
/pos
```

Desktop-first layout:

```text
┌────────────────────────────────────────────────────┐
│ POS Header                                          │
├──────────────────────────────┬─────────────────────┤
│ Product Search / Barcode     │ Cart                │
│                              │                     │
│ Product Grid                 │ Items               │
│                              │ Qty                 │
│                              │ Discount            │
│                              │ Tax                 │
│                              │ Total               │
├──────────────────────────────┴─────────────────────┤
│ Customer | Payment | Hold | Clear | Generate Bill  │
└────────────────────────────────────────────────────┘
```

Features:

- Barcode input
- Product search
- Quick product buttons
- Quantity
- Discount
- GST
- Customer selection
- Cash
- UPI
- Card
- Split payment if later required
- Generate invoice
- Print invoice
- Hold cart
- Resume cart
- Clear cart

---

# 34. POS Payment UI

Payment modal:

```text
Grand Total
Customer
Cash
UPI
Card
Amount Received
Change
Confirm Payment
```

After successful payment:

```text
Payment Successful
Invoice Number
Print
Download
New Sale
```

---

# 35. POS Sales History

Columns:

```text
Invoice
Date
Customer
Items
Amount
Payment
Cashier
Status
Actions
```

Actions:

```text
View
Print
Return
```

---

# 36. POS Day Closing

Show:

```text
Opening Cash
Cash Sales
UPI Sales
Card Sales
Returns
Expected Cash
Actual Cash
Difference
```

Then:

```text
Close POS Session
```

---

# 37. UI-09 — Support Panel

Route:

```text
/support
```

Dashboard:

```text
Open Tickets
High Priority
In Progress
Resolved Today
SLA Breaches
```

Ticket list:

```text
Ticket ID
Subject
Customer
Category
Priority
Assigned To
Status
Created
```

Ticket details:

```text
Customer information
Issue
Attachments
Conversation
Internal notes
Assignment
Status
Resolution
```

---

# 38. UI-10 — Tech Mitra Panel

Route:

```text
/tech-mitra
```

Dashboard:

```text
Today's Jobs
Pending
Accepted
In Progress
Completed
Today's Earnings
```

Pages:

```text
/tech-mitra/jobs
/tech-mitra/jobs/:id
/tech-mitra/calendar
/tech-mitra/customers
/tech-mitra/history
/tech-mitra/earnings
/tech-mitra/profile
```

---

# 39. Tech Mitra Job Details

Show:

```text
Customer
Phone
Address
Location
Product
Problem
Service Type
Scheduled Time
AMC Status
```

Job actions:

```text
Accept
Reject
On the Way
Reached
Start Service
Pause
Complete
```

Service form:

```text
Diagnosis
Work Done
Parts Used
Labour
Customer Notes
Before Photo
After Photo
Customer OTP
Customer Signature
```

---

# 40. UI-11 — AMC

Customer:

```text
/amc
```

Show:

- AMC plans
- Coverage
- Price
- Duration
- Benefits
- Buy AMC

Customer active AMC:

```text
Plan
Start Date
Expiry Date
Services Used
Services Remaining
Coverage
Renew
```

Admin AMC:

```text
/amc/plans
/amc/subscriptions
/amc/usage
/amc/reports
```

---

# 41. Service Booking UI

Customer service flow:

```text
Select Product
   ↓
Select Service
   ↓
Describe Problem
   ↓
Address
   ↓
Date & Time
   ↓
AMC / Paid Service
   ↓
Confirm
```

Service tracking:

```text
Requested
Assigned
Accepted
On The Way
Reached
In Progress
Completed
```

---

# 42. Returns UI

Customer:

```text
My Order
   ↓
Request Return
   ↓
Select Item
   ↓
Reason
   ↓
Upload Image
   ↓
Submit
```

Admin:

```text
Pending
Review
Approved
Rejected
Product Received
Inspection
Refund
Replacement
Completed
```

Use a visual timeline.

---

# 43. Reports UI

Reusable report layout:

```text
Date Filter
Store Filter
Franchise Filter
Product Filter
Export
```

Reports:

- Sales
- Revenue
- Products
- Inventory
- Franchise
- Store
- Distribution
- Services
- Tech Mitra
- AMC
- Returns

Charts:

- Line chart
- Bar chart
- Donut chart
- Area chart

Charts must remain readable in dark mode.

---

# 44. Settings UI

Sections:

```text
General
Branding
Theme
Users
Roles
Permissions
Notifications
Payment
Shipping
Tax
Service
AMC
POS
Security
```

Theme settings:

```text
Light
Dark
System
Primary Color
```

If custom primary colors are implemented later, they must update CSS variables rather than individual components.

---

# 45. Login / Authentication UI

Pages:

```text
/login
/register
/forgot-password
/reset-password
```

Login:

```text
ComCare Logo
Email / Phone
Password
Remember Me
Login
Forgot Password
```

Role-based redirect can use mock behavior for now.

---

# 46. Franchise Application UI

Because ComCare's goal includes providing franchises, include a public franchise page:

```text
/franchise
/franchise/apply
```

Franchise landing:

```text
Hero
Why ComCare
Business Model
Benefits
Investment Information
Support
Training
Technology
FAQ
Apply Now
```

Application form:

```text
Personal Information
Business Information
Location
Investment Capacity
Preferred Store Location
Documents
Submit Application
```

---

# 47. Public Marketing Pages

Create:

```text
/
 /about
 /contact
 /services
 /franchise
 /franchise/apply
 /privacy
 /terms
 /faq
```

Footer:

```text
ComCare
Quick Links
Products
Services
Franchise
Support
Contact
Social Links
Legal
```

---

# 48. Responsive Design

Every page must support:

```text
Mobile
Tablet
Laptop
Desktop
Large Desktop
```

Breakpoints should follow Tailwind conventions unless there is a strong reason to customize them.

## Mobile rules

- Sidebar → drawer
- Tables → horizontal scroll or card layout
- POS → optimized tablet/mobile layout
- Filters → bottom sheet/drawer
- Multi-column dashboard → single column
- Buttons → touch-friendly
- Inputs → full width where appropriate

---

# 49. Accessibility

Minimum requirements:

- Semantic HTML
- Keyboard navigation
- Visible focus states
- Proper labels
- Alt text
- Sufficient contrast
- ARIA where needed
- Do not rely only on color to communicate status

Example:

Bad:

```text
Red = Failed
```

Better:

```text
[Failed] + icon + text
```

---

# 50. Loading / Error / Empty States

Every data-driven screen should have:

### Loading

Skeleton UI.

### Empty

Example:

```text
No purchase requests yet.
Create your first purchase request.
```

### Error

```text
Something went wrong.
Try Again
```

### Success

Use toast/confirmation.

---

# 51. Mock Data Rule

Before API integration, use local mock data.

Recommended:

```text
src/mock/
├── products.js
├── orders.js
├── stores.js
├── franchises.js
├── purchaseRequests.js
├── services.js
├── technicians.js
└── tickets.js
```

Do not hard-code large data arrays directly inside page components.

---

# 52. Routing Architecture

Use React Router.

Organize routes by area:

```text
src/routes/
├── publicRoutes.jsx
├── customerRoutes.jsx
├── adminRoutes.jsx
├── distributionRoutes.jsx
├── franchiseRoutes.jsx
├── storeRoutes.jsx
├── posRoutes.jsx
├── supportRoutes.jsx
└── techMitraRoutes.jsx
```

Protected route components should be designed now even though real authentication API is not connected.

---

# 53. Component Architecture

Recommended:

```text
src/
├── components/
│   ├── common/
│   ├── forms/
│   ├── tables/
│   ├── charts/
│   ├── navigation/
│   ├── ecommerce/
│   ├── dashboard/
│   ├── pos/
│   ├── service/
│   └── theme/
│
├── layouts/
│   ├── PublicLayout.jsx
│   ├── DashboardLayout.jsx
│   ├── POSLayout.jsx
│   └── AuthLayout.jsx
│
├── pages/
│   ├── public/
│   ├── customer/
│   ├── admin/
│   ├── distribution/
│   ├── franchise/
│   ├── store/
│   ├── pos/
│   ├── support/
│   └── tech-mitra/
```

---

# 54. Do Not Duplicate UI

If two pages use the same:

- Table
- Modal
- Filter
- Page header
- Status badge
- Stat card
- Form

create a reusable component.

---

# 55. Business Status Colors

Brand red is the main action color, but statuses should remain distinguishable.

Suggested:

```text
Success → Green
Warning → Amber
Danger → Red
Info → Blue
Neutral → Gray
```

Dark mode must preserve readable contrast.

---

# 56. UI Data Relationships

The UI should visually represent:

```text
Super Admin
    ↓
Franchise
    ↓
Store
    ↓
Store Inventory
    ↓
POS
    ↓
Customer Sale
```

and:

```text
Central Warehouse
    ↓
Distribution
    ↓
Purchase Request
    ↓
Dispatch
    ↓
Store
```

and:

```text
Customer
    ↓
Service Request
    ↓
Tech Mitra
    ↓
Service
    ↓
Completion
```

---

# 57. Important UI Business Separation

Never visually mix:

### Product Sale

```text
POS
```

with:

### Service

```text
Service Management
```

and:

### Central Stock Supply

```text
Distribution
```

These are separate business modules.

---

# 58. UI Phase Completion Checklist

A phase is complete only when:

- [ ] Pages created
- [ ] Routes created
- [ ] Navigation works
- [ ] Mock data works
- [ ] Loading states exist
- [ ] Empty states exist
- [ ] Error states exist
- [ ] Light mode works
- [ ] Dark mode works
- [ ] Responsive layout works
- [ ] No obvious console errors
- [ ] Reusable components used
- [ ] No unnecessary duplicate code
- [ ] Theme colors come from centralized CSS variables

---

# 59. Final UI Folder Target

After all UI phases, aim for:

```text
frontend/
└── src/
    ├── assets/
    ├── components/
    │   ├── common/
    │   ├── dashboard/
    │   ├── ecommerce/
    │   ├── pos/
    │   ├── service/
    │   ├── tables/
    │   └── theme/
    │
    ├── context/
    │   └── ThemeContext.jsx
    │
    ├── layouts/
    │   ├── PublicLayout.jsx
    │   ├── DashboardLayout.jsx
    │   ├── POSLayout.jsx
    │   └── AuthLayout.jsx
    │
    ├── mock/
    ├── pages/
    ├── routes/
    ├── styles/
    │   ├── theme.css
    │   ├── globals.css
    │   └── components.css
    │
    ├── App.jsx
    └── main.jsx
```

---

# 60. UI-Only Development Rule

Until the UI is approved:

DO:

- React
- Tailwind CSS
- CSS variables
- mock data
- local state
- React Router
- reusable components
- responsive UI

DO NOT:

- connect DRF
- create API services
- create real authentication
- create database models
- depend on backend endpoints
- build payment integration
- build real GPS
- build real notifications

Those belong to the integration/backend phase.

---

# 61. API Integration Will Start Later

After UI approval:

```text
UI Page
   ↓
Identify required data
   ↓
Database Model
   ↓
DRF Serializer
   ↓
DRF API
   ↓
Permission
   ↓
Frontend API service
   ↓
Replace mock data
   ↓
Integration testing
```

Do not design APIs blindly before the final UI requirements are clear.

---

# 62. FINAL UI DEVELOPMENT ORDER

```text
START
  ↓
UI-01 Theme + Design System
  ↓
UI-02 Shared Layout
  ↓
UI-03 Customer eCommerce
  ↓
UI-04 Super Admin
  ↓
UI-05 Distribution
  ↓
UI-06 Franchise
  ↓
UI-07 Store Admin
  ↓
UI-08 POS
  ↓
UI-09 Support
  ↓
UI-10 Tech Mitra
  ↓
UI-11 AMC
  ↓
UI-12 Public Franchise + Marketing
  ↓
UI-13 Responsive + Accessibility
  ↓
UI-14 Final UI Review
  ↓
STOP
  ↓
BACKEND + DRF API PHASE
```

---

# 63. FIRST TASK FOR THE UI AGENT

When starting this document with an AI coding agent:

### FIRST RUN — ONLY UI-01

The agent must:

1. Inspect the existing React + Tailwind project.
2. Do not rebuild the existing project unnecessarily.
3. Create the centralized theme architecture.
4. Create `src/styles/theme.css`.
5. Create global styling.
6. Add ComCare red/black/white brand system.
7. Add light/dark/system mode.
8. Add persistent theme selection.
9. Create ThemeToggle.
10. Create basic reusable UI components.
11. Verify the frontend builds successfully.
12. Verify dark mode.
13. Verify responsive behavior.
14. STOP.

Do NOT build dashboards in the first task.

---

# 64. Agent Working Rules

The coding agent must follow these rules:

1. Read this MD before every UI phase.
2. Inspect existing files before modifying them.
3. Never overwrite working code without reason.
4. Never build all pages in one go.
5. Never jump to another phase automatically.
6. Use reusable components.
7. Use centralized theme variables.
8. Keep light/dark mode consistent.
9. Use mock data until API phase.
10. Run the project after meaningful changes.
11. Fix errors before declaring a phase complete.
12. At the end of a phase, report changes and STOP.

---

# 65. Definition of Done

The UI phase is complete only when a user can navigate the entire ComCare frontend visually without a backend:

```text
Public Website
      ↓
Customer
      ↓
Super Admin
      ↓
Distribution
      ↓
Franchise
      ↓
Store Admin
      ↓
POS
      ↓
Support
      ↓
Tech Mitra
      ↓
AMC
```

All pages must use the same:

- Brand
- Typography
- Spacing
- Components
- Theme
- Dark mode
- Responsive behavior

The final result should look like **one professional ComCare product**, not a collection of unrelated dashboards.
