# HTMX + Alpine.js Architecture Document
## ComCare — E-Commerce Platform

> Ye doc tumhare actual project code (`ComCare_it/`) ko scan karke banaya gaya hai — jo already implement ho chuka hai wahi base hai, kalpana ke patterns nahi. Goal: jo achha pattern already chal raha hai use standardize karna, aur jo inconsistent/adhoora hai use fix karne ka clear raasta dena — bina kuch tod ke.

---

## 1. Current Setup (base.html)

```html
<!-- HTMX -->
<script src="https://unpkg.com/htmx.org@1.9.10"></script>

<!-- Alpine.js -->
<script defer src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js"></script>

<!-- Lucide Icons -->
<script src="https://unpkg.com/lucide@latest"></script>
```

Icons ke liye ek smart global re-init pattern already hai — isse chhedna nahi, ye sabse important cross-cutting piece hai:

```html
<script>
    function refreshIcons() {
        if (window.lucide && typeof window.lucide.createIcons === 'function') {
            window.lucide.createIcons();
        }
    }
    window.refreshIcons = refreshIcons;
    document.addEventListener('DOMContentLoaded', refreshIcons);
    window.addEventListener('load', refreshIcons);
    document.addEventListener('alpine:init', refreshIcons);
    document.addEventListener('alpine:initialized', refreshIcons);
    document.addEventListener('htmx:afterSettle', refreshIcons);
</script>
```

**Rule:** Koi bhi naya HTMX swap ya Alpine component banao, iske baare mein alag se sochne ki zaroorat nahi — `htmx:afterSettle` already har HTMX swap ke baad icons re-render kar deta hai. Sirf ye dhyan rakhna ki naya partial HTML mein `data-lucide="..."` tags ho, baaki apne aap ho jayega.

---

## 2. Core Principle — Kaam Kisका Hai

| Zimmedari | Tool | Kyun |
|---|---|---|
| Server se data laana/bhejna, DB update, list re-render | **HTMX** | Server truth ka source hai, client ko dobara HTML banane ki zaroorat nahi |
| Sirf visual/UI state — tab switch, modal open/close, dropdown, image gallery, quantity stepper (jo submit se pehle sirf UI mein hai) | **Alpine.js** | Koi server round-trip nahi chahiye |
| Dono ek saath (state bhi, data bhi) | **Alpine (UI shell) + HTMX (data fetch/submit)** | Jaisa `product_card_body.html` mein `x-data="{ inWishlist }"` + button wishlist ke andar hai |

**Golden rule jo already project mein prove ho chuka hai (shop.html, product cards, cart):**
> Agar result HTML hai jo user ko dikhna hai → HTMX se server render karke laao.
> Agar result sirf ek boolean/toggle/tab hai jo abhi ke DOM mein hi reflect hona hai → Alpine se.

---

## 3. Established Patterns (Already Working — In Production)

Ye woh patterns hain jo tumhare project mein **already chal rahe hain aur sahi hain**. Naya kaam karte waqt inhi ko copy karo.

### Pattern A — "Add to Cart" with Out-of-Band (OOB) Swap
**Files:** `templates/partials/product_card_body.html`, `templates/partials/ajax_add_card_response.html`, `apps/cart/views.py::add_cart_ajax`

Ek hi HTMX request se 3 jagah update ho jati hai — button khud, header cart badge, aur toast — bina kisi extra JS ke:

```html
<!-- Trigger button (product card) -->
<button
    hx-get="{% url 'add_cart_ajax' card_id %}?view=card"
    hx-swap="outerHTML">
    Add
</button>
```

```html
<!-- Server response: ajax_add_card_response.html -->
<a href="{% url 'cart' %}">Go to Cart</a>

<!-- OOB swap #1: header badge, kahin bhi ho, apne aap update -->
<span id="header-cart-badge" hx-swap-oob="true">{{ cart_count }}</span>

<!-- OOB swap #2: toast, container ke end mein insert -->
<div id="toast-container" hx-swap-oob="beforeend">
    <div x-data="{ show: true }" x-show="show" x-init="setTimeout(() => show = false, 1000)" x-transition:leave="...">
        Item added to cart!
    </div>
</div>
```

**Yehi pattern reuse karo har jagah jahan "ek action → multiple UI jagah update" chahiye** (jaise: return request submit → order card update + toast; coupon apply → cart summary + toast).

### Pattern B — Cart Quantity ± / Remove (Full Container Re-render)
**Files:** `templates/partials/cart_container.html`, `apps/cart/views.py::add_cart/remove_cart/remove_cart_item`

```html
<button hx-get="{% url 'remove_cart' item.product.id %}" hx-target="#cart-container" hx-swap="innerHTML">-</button>
<button hx-get="{% url 'add_cart' item.product.id %}" hx-target="#cart-container" hx-swap="innerHTML">+</button>
```

View poora `cart_container.html` partial re-render karta hai (naya total, tax, coupon discount, sab recalculate ho ke aata hai). Simple, reliable — chhote cart ke liye (~10-20 items) ye best approach hai, single-item DOM patching se zyada maintain-friendly.

### Pattern C — Coupon Apply/Remove
**File:** `templates/partials/cart_container.html`

```html
<form hx-post="{% url 'apply_coupon' %}" hx-target="#cart-container" hx-swap="innerHTML">
    {% csrf_token %}
    <input type="text" name="coupon_code">
    <button type="submit">Apply</button>
</form>
```
Same target/swap jaisa Pattern B — same container, isliye coupon error/success bhi automatically consistent state mein render hota hai.

### Pattern D — Live Search Preview (Debounced)
**File:** `templates/partials/header.html`, `templates/partials/search_preview_fragment.html`

```html
<input
    type="text" name="q" x-model="searchQuery"
    @focus="searchFocused = true" @click.away="searchFocused = false"
    hx-get="{% url 'search' %}"
    hx-trigger="keyup changed delay:300ms, search"
    hx-target="#search-results-preview">

<div x-show="searchFocused && searchQuery.trim().length > 0" x-transition>
    <div id="search-results-preview"></div>
</div>
```
Yahan Alpine sirf dropdown ka **visibility** control kar raha hai (`searchFocused`, `x-model` for reactivity check), HTMX data laa raha hai. Ye textbook combo hai — isko template banao naye kisi bhi "type → live results" feature ke liye (jaise admin panel mein customer search, product search).

### Pattern E — Infinite Scroll Pagination
**File:** `apps/store/templates/shop.html`

```html
<div class="contents"
    hx-get="{% url 'shop' %}?page={{ page_obj.next_page_number }}{% if url_params %}&{{ url_params }}{% endif %}"
    hx-trigger="revealed"
    hx-swap="outerHTML"
    hx-indicator="#infinite-spinner">
    {% include 'partials/product_card.html' with product=product %}
</div>
```
`hx-trigger="revealed"` last card pe laga hai — jab wo viewport mein aata hai, agla page load ho jata hai. Clean pattern, koi issue nahi.

### Pattern F — Wishlist Toggle (Raw `fetch()`, HTMX nahi)
**Files:** `product_card_body.html`, `product_detail.html`, `wishlist.html`

Ye ek jagah HTMX use nahi hota — plain `fetch()` + Alpine state update:

```js
@click.prevent="
    fetch('/account/wishlist/toggle/' + ({{ card_id }}) + '/', {
        method: 'POST',
        headers: { 'X-CSRFToken': '{{ csrf_token }}', 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            inWishlist = data.in_wishlist;
            document.querySelectorAll('#header-wishlist-badge').forEach(el => el.textContent = data.wishlist_count);
        }
    });
"
```

**Ye jaan-boojh kar HTMX se nahi hai kyunki:** wishlist heart button ka visual state (`fill-rose-500`) turant, bina kisi HTML re-render ke, sirf Alpine reactivity se change hona chahiye — aur `document.querySelectorAll` se **multiple heart icons** (agar ek hi product card page pe 2 jagah dikhe) ek saath sync hote hain, jo HTML swap se possible nahi hota asaani se.

> Iska matlab ye nahi ki ye galat hai — ye ek **valid, alag pattern** hai jab tumhe "instant visual toggle + JSON data" chahiye ho, HTML fragment nahi. Isse "Pattern F: JSON Toggle" naam de do aur consciously use karo, accident se nahi.

---

## 4. ⚠️ Inconsistency Jo Fix Karni Chahiye

Do jagah **Pattern F jaisa fetch+JSON approach** use hua hai jahan actually **Pattern A/B jaisa HTMX + server-rendered-HTML** better fit karta:

### 4.1 `apps/accounts/templates/addresses.html`
- Poora `saveAddress()`, `deleteAddress()`, `setDefault()` — raw `fetch()` + manual `buildCardHTML()` JS function jo client-side pe HTML string banata hai.
- Ye maintain karna mushkil hai: koi bhi card HTML change karo, tumhe do jagah change karna padta hai — Django template mein bhi, `buildCardHTML()` JS string mein bhi. Bug ka sabse common source yahi hota hai.
- **`pending_work.md` mein ye item #4 pe already flagged hai** ("Static Dummy Data").

### 4.2 `apps/cart/templates/checkout.html`
- Address select/add/edit/delete — same `fetch()` pattern, `checkoutApp()` Alpine function ke andar.
- Yahan bhi `UserAddress` model (`apps/cart/models.py`) se related saara CRUD JSON se ho raha hai.

### Fix — Section 6 mein exact migration diya hai (`address_card.html` partial banake).

---

## 5. Naye Feature Ke Liye Decision Flowchart

```
Kya action se koi data change hota hai (DB) jo screen pe dikhna hai?
│
├── NAHI → sirf UI/visual state (modal, tab, toggle, image switch)
│         └── Alpine.js — x-data + x-show/x-model, koi network call nahi
│
└── HAAN → data change hota hai
    │
    ├── Result: HTML fragment jo directly render ho sakta hai
    │           (list, card, form-with-errors, updated total)
    │   └── HTMX — hx-get/hx-post + hx-target + hx-swap
    │       (agar 1+ jagah update karni ho → hx-swap-oob)
    │
    └── Result: sirf ek chhota flag/count jo turant, animation-free,
                multiple places sync hona chahiye (jaise heart icon)
        └── raw fetch() + Alpine state (Pattern F) — sparingly use karo
```

---

## 6. Module-by-Module Architecture

### 6.1 Global (Header, Footer, Toasts)
| Component | Tool | Detail |
|---|---|---|
| Mobile menu, user dropdown, category dropdown | Alpine | `x-data` on header root: `mobileMenuOpen, userDropdownOpen, categoryOpen` |
| Dark mode toggle | Alpine + `localStorage` | Already working, theme flash-prevention script bhi hai |
| Live search preview | Alpine (visibility) + HTMX (data) | Pattern D |
| Cart/Wishlist header badge | HTMX OOB swap | `#header-cart-badge`, `#header-wishlist-badge` — kahin se bhi `hx-swap-oob="true"` se update |
| Toast notifications | HTMX OOB (`beforeend`) + Alpine (auto-dismiss) | Pattern A — reuse everywhere |

### 6.2 Shop / Filters (`shop.html`)
**Current state (important!):** Sidebar filters (`cat`, `brand`, `price`, `stock`) Alpine se `document.getElementById('filter-form').submit()` call karke **poore page ka GET reload** karte hain — HTMX nahi. `isFiltering` Alpine variable sirf ek **skeleton shimmer** dikhata hai reload hone tak.

Sirf **infinite-scroll pagination** (Pattern E) actual HTMX hai.

> PRD mein likha hai "filter search — all HTMX powered" — abhi codebase mein aisa nahi hai. Ye MVP ke liye chal sakta hai (SEO-friendly URLs milte hain, bookmark-able filter links), par agar tum truly HTMX filtering chahte ho:

**Recommended upgrade (optional, non-breaking):**
```html
<form id="filter-form"
    hx-get="{% url 'shop' %}"
    hx-target="#product-grid"
    hx-swap="innerHTML"
    hx-push-url="true"
    @submit="isFiltering = true">
```
View mein check karo `request.headers.get('HX-Request')` — agar true hai to sirf `product_list_fragment.html` return karo, warna poora `shop.html`. Ye tumhare `product_list_fragment.html` (already exists!) ko real use dega — abhi wo file bani hui hai but shop.html use nahi karta, sirf pagination inline duplicate karta hai.

### 6.3 Product Card / Product Detail
| Action | Tool |
|---|---|
| Add to cart | HTMX (Pattern A) |
| Wishlist toggle | fetch + Alpine (Pattern F) |
| Image gallery (thumbnail → main image) | Alpine (`activeImage`) |
| Description/Spec/Reviews tabs | Alpine (`activeTab`) |
| Quantity stepper (before add-to-cart) | Alpine, phir `hx-include="#product-qty-input"` se HTMX request mein bhej diya jata hai |

### 6.4 Cart & Coupons
Fully HTMX — Patterns A/B/C. Ye project ka **sabse achha reference implementation** hai. Koi change nahi chahiye.

### 6.5 Checkout (`checkout.html`)
- Address CRUD: currently fetch+JSON (Section 4.2) → **migrate to HTMX** (Section 7)
- Payment method toggle (Razorpay vs COD): Alpine `paymentMethod` variable — sahi hai, koi issue nahi
- Order placement (`submitOrder()`): fetch() se `place_order` aur `verify_payment` — **ye theek hai as-is**, kyunki Razorpay ka JS SDK khud bhi async callback-based hai aur HTMX ke saath mix karna unnecessary complexity add karega. Payment flow ko fetch/JS mein hi rakho.

### 6.6 Account Dashboard (Profile, Addresses, Orders, Wishlist, Change Password)
| Page | Current State | Target |
|---|---|---|
| `addresses.html` | fetch+JSON, `buildCardHTML()` | → HTMX (Section 7) |
| `orders.html` | Alpine sirf modal state (`showReturnModal`, `showCancelModal`) — return/cancel ka actual submit abhi likhna baaki hai (pending_work #2, #7) | HTMX form POST → target order card partial |
| `wishlist.html` | fetch+JSON toggle (Pattern F, consistent) | Keep as-is |
| `profile.html` | Static (pending_work #1) | Plain Django form POST (page reload theek hai) ya HTMX form → target profile card |
| `change_password.html` | Static, Alpine-only fake success (pending_work #2) | HTMX form POST → target message div |

### 6.7 Admin Panel
**Important finding:** Saare admin views (`apps/admin/views.py`) abhi sirf `render(request, 'admin_x.html')` hain — **koi POST handling, koi DB query, kuch nahi**. Sab kuch static/dummy hai. `x-data="{ showProductModal: false }"` jaisi Alpine states sirf modal open/close karti hain, andar ka form kahin submit nahi hota.

Ye pura module banana baaki hai. Jab banao, to **exactly `apps/accounts` ke naye address pattern ki tarah** karo (Section 7):
- List page → context mein queryset pass karo
- Add/Edit modal → HTMX form → server-rendered row/card partial return
- Delete → `hx-delete` + `hx-confirm` + `hx-swap="outerHTML swap:0.3s"` (row fade-out)
- Bulk actions/filters → HTMX GET with `hx-target` on table body

### 6.8 Contact / Services Forms
`contact.html` (`x-data="{ messageSent: false }"`) aur `services.html` — abhi Alpine-only fake success state ya plain form (verify karna padega actual POST view). **Recommendation:** simple HTMX POST → return ek small "Thank you, we'll call you" partial, `messageSent` Alpine flag hata do, kyunki HTMX response khud hi conditionally success/error partial de sakta hai.

---

## 7. Concrete Fix — Addresses (Accounts + Checkout dono)

Ye woh exact refactor hai jo maine pehle discuss kiya tha, ab tumhare real `UserAddress` model (`apps/cart/models.py`) aur `apps/cart/views.py` ke against likha hai.

### 7.1 Naya partial: `apps/cart/templates/partials/address_card.html`
```html
<div id="addr-card-{{ addr.id }}"
     class="bg-white p-6 rounded-3xl border-2 {% if addr.is_default %}border-[var(--color-primary)]{% else %}border-gray-200{% endif %} shadow-sm">
    <div class="flex items-center justify-between">
        <h3 class="font-bold text-sm">{{ addr.full_name }}</h3>
        {% if addr.is_default %}<span class="bg-emerald-50 text-emerald-700 text-[10px] font-bold px-2.5 py-0.5 rounded-full">Default</span>{% endif %}
    </div>
    <p class="text-xs text-gray-500 mt-2">
        {{ addr.address_line1 }}{% if addr.address_line2 %}, {{ addr.address_line2 }}{% endif %},<br>
        {{ addr.city }}, {{ addr.state }} — {{ addr.pincode }}
    </p>
    <div class="text-xs text-gray-500 mt-2">Phone: <strong>{{ addr.phone }}</strong></div>

    <div class="flex items-center justify-between border-t border-gray-100 pt-3 mt-3 text-xs">
        <div class="flex gap-4">
            <button type="button" class="text-[var(--color-primary)] font-bold"
                @click="openEditModal({{ addr.id }})">Edit</button>
            <button class="text-red-500 font-bold"
                hx-post="{% url 'delete_address' addr.id %}"
                hx-target="#addr-card-{{ addr.id }}"
                hx-swap="outerHTML swap:0.3s"
                hx-confirm="Are you sure you want to delete this address?">
                Delete
            </button>
        </div>
        {% if not addr.is_default %}
        <button class="text-[var(--color-primary)] text-[11px] font-semibold"
            hx-post="{% url 'set_default_address' addr.id %}"
            hx-target="#address-grid" hx-swap="innerHTML">
            Set as Default
        </button>
        {% endif %}
    </div>
</div>
```

### 7.2 `addresses.html` — sirf grid include karo
```html
<div id="address-grid" class="grid grid-cols-1 md:grid-cols-2 gap-6">
    {% for addr in addresses %}
        {% include 'partials/address_card.html' with addr=addr %}
    {% endfor %}
</div>
```

Alpine sirf modal ke liye reh jayega (`showModal`, `editMode`, `form.*` fields for `x-model`) — save button `hx-post` se hoga, **`buildCardHTML()` function poora delete**.

```html
<form
    hx-post="{% url 'save_address' %}"
    hx-target="#address-grid"
    hx-swap="beforeend"
    @htmx:after-request="showModal = false">
    {% csrf_token %}
    <input type="hidden" name="address_id" x-bind:value="editId">
    <input type="text" name="full_name" x-model="form.full_name" required>
    <!-- ...baaki fields same... -->
</form>
```

### 7.3 View — `save_address` ab HTML return karega, JSON nahi
`apps/cart/views.py` mein:
```python
def save_address(request):
    if request.method == "POST":
        address_id = request.POST.get('address_id')
        if address_id:
            addr = get_object_or_404(UserAddress, id=address_id, user=request.user)
        else:
            addr = UserAddress(user=request.user)

        addr.full_name = request.POST.get('full_name')
        addr.phone = request.POST.get('phone')
        addr.email = request.POST.get('email', '')
        addr.address_line1 = request.POST.get('address_line1')
        addr.address_line2 = request.POST.get('address_line2', '')
        addr.city = request.POST.get('city')
        addr.state = request.POST.get('state')
        addr.pincode = request.POST.get('pincode')
        addr.address_type = request.POST.get('address_type', 'home')
        is_default = request.POST.get('is_default') == 'true'

        if is_default:
            UserAddress.objects.filter(user=request.user).update(is_default=False)
        addr.is_default = is_default
        addr.save()

        # Edit case: replace existing card in-place instead of appending
        if address_id:
            return render(request, 'partials/address_card.html', {'addr': addr})
        return render(request, 'partials/address_card.html', {'addr': addr})
```

Edit ke liye form ka `hx-target`/`hx-swap` dynamically Alpine se set karo (`x-bind:hx-target`, ya do alag forms — add/edit) — ya simplest: **edit ke liye alag inline `hx-post` on the same form with `hx-target="#addr-card-{editId}"` jab `editMode=true` ho, aur `hx-swap="outerHTML"`.** Alpine se `hx-target`/`hx-swap` ko `x-bind` karke dynamic banaya ja sakta hai:

```html
<form
    hx-post="{% url 'save_address' %}"
    x-bind:hx-target="editMode ? ('#addr-card-' + editId) : '#address-grid'"
    x-bind:hx-swap="editMode ? 'outerHTML' : 'beforeend'"
    hx-trigger="submit"
    @htmx:after-request="showModal = false">
```
> Note: `x-bind:hx-*` set hone ke baad HTMX ko process karwane ke liye `htmx.process(el)` call karna padega Alpine `x-init` mein, kyunki HTMX attributes ko dynamically bind karne pe HTMX unhe re-scan nahi karta apne aap. Simplest safe alternative: **do separate `<form>` blocks** — ek Add ke liye fixed target `#address-grid`, ek Edit ke liye `x-show="editMode"` ke saath fixed target `#addr-card-{{ editId }}` (Django se render nahi hoga kyunki editId Alpine variable hai — is case mein generic wrapper target `#address-grid` with `hx-swap="innerHTML"` aur poora list re-render sabse safe hai, jaisa cart karta hai). **Recommendation: dono add/edit ke liye `hx-target="#address-grid" hx-swap="innerHTML"` rakho aur view se poori list return karo** — Pattern B jaisa hi, simplicity ke liye consistency behtar hai speed ke chhote optimization se.

### 7.4 Same exact pattern → `checkout.html`
Checkout mein address section ko bhi isi `address_card.html` (ya checkout-specific variant, radio-selection wala) partial se replace karo, `#address-grid` ko checkout page ke apne address list container se target karo. `save_address`/`delete_address` views already shared hain (`apps/cart/urls.py`), sirf response format HTML kar do — dono jagah (account addresses + checkout) same view reuse ho jayega, do baar maintain nahi karna padega.

---

## 8. Naming Conventions (Follow Karo Aage Se)

| Type | Convention | Example |
|---|---|---|
| Partial templates | `templates/partials/<noun>_<purpose>.html` | `address_card.html`, `order_row.html` |
| HTMX response-only partials (OOB wale) | `partials/ajax_<action>_response.html` | already followed: `ajax_add_card_response.html` |
| Container IDs (HTMX target) | `#<noun>-grid`, `#<noun>-container` | `#address-grid`, `#cart-container` (already followed) |
| Row/card IDs (individual item) | `#<noun>-card-{{ id }}` | `#addr-card-{{ addr.id }}`, `#product-card-{{ product.id }}` |
| Alpine component functions | `<page>Page()` / `<page>App()` | already followed: `addressPage()`, `checkoutApp()` |

---

## 9. Quick Checklist — Naya Feature Banate Waqt

1. Pehle poocho: *is action ka result HTML hai ya sirf ek flag?*
2. HTML hai → partial template banao `templates/partials/` mein, view se `render()` karo (JsonResponse nahi)
3. Container ko stable `id` do — `hx-target` isi pe point karega
4. Agar ek action se 2+ jagah update karni hai (badge, toast, list) → OOB swap use karo, JS mat likho
5. Sirf tab/modal/toggle hai → Alpine, koi network call nahi
6. Delete action → `hx-confirm` + `hx-swap="outerHTML swap:0.3s"` (fade-out animation free milta hai)
7. Naye icons use kiye → kuch mat karo, `htmx:afterSettle` already handle karta hai

---

## 10. Priority Order (`pending_work.md` ke against)

| # | Item | HTMX/Alpine Action Needed |
|---|---|---|
| 1 | Profile update | Plain form POST ya HTMX form → target profile card |
| 2 | Change password | HTMX form POST → target `#password-msg` div |
| 4 | Addresses (accounts) | Section 7 — full migration |
| 6 | Guest checkout address | Checkout mein Section 7 wala inline form reuse |
| 7 | Return request | HTMX form (already `showReturnModal` Alpine state hai orders.html mein) → POST → target order card |
| 9 | Shop filters verify | Section 6.2 — optional upgrade to true HTMX |
| 12 | Admin order status | Section 6.7 — poora module HTMX se banao |
| 14 | Reviews system | Naya form, Pattern A jaisa (submit → review list partial + toast) |

---

*Doc generated from live scan of `ComCare_it/` codebase — apps: accounts, admin, cart, categories, core, coupons, services, store.*