from decimal import Decimal
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from apps.cart.models import Cart, CartItem, Order, OrderItem, ShippingConfig, UserAddress
from apps.coupons.models import Coupon
from apps.store.models import Product


def get_guest_session_key(request):
    """
    Extracts guest cart session key from request headers, query string, or Django session.
    """
    header_key = request.headers.get('X-Guest-Cart-Key', '').strip()
    if header_key:
        return header_key
    param_key = request.GET.get('guest_key', '').strip()
    if param_key:
        return param_key
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_or_create_cart(user=None, session_key=None, create=False):
    """
    Retrieves or creates active cart for user or guest session_key.
    Re-associates guest cart with user upon authentication.
    """
    cart = None

    if user and user.is_authenticated:
        cart = Cart.objects.filter(Q(user=user) | (Q(session_key=session_key) & Q(session_key__isnull=False))).order_by('-updated_at').first()
        if cart:
            updated = False
            if cart.user != user:
                cart.user = user
                updated = True
            if session_key and cart.session_key != session_key:
                cart.session_key = session_key
                updated = True
            if updated:
                cart.save()
        elif create:
            cart = Cart.objects.create(user=user, session_key=session_key)
    elif session_key:
        cart = Cart.objects.filter(session_key=session_key).order_by('-updated_at').first()
        if not cart and create:
            cart = Cart.objects.create(session_key=session_key)

    return cart


def merge_guest_cart(user, session_key):
    """
    Merges all items from a guest session cart into the logged-in user's cart.
    """
    if not user or not user.is_authenticated or not session_key:
        return None

    guest_cart = Cart.objects.filter(session_key=session_key, user__isnull=True).first()
    if not guest_cart:
        return get_or_create_cart(user=user, session_key=session_key, create=True)

    user_cart, _ = Cart.objects.get_or_create(user=user, defaults={'session_key': session_key})

    guest_items = CartItem.objects.filter(cart=guest_cart)
    for g_item in guest_items:
        u_item, created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=g_item.product,
            defaults={
                'quantity': g_item.quantity,
                'unit_price': g_item.unit_price or g_item.product.selling_price,
                'is_active': True
            }
        )
        if not created:
            u_item.quantity += g_item.quantity
            u_item.save()

    guest_cart.delete()
    return user_cart


def apply_coupon_to_subtotal(code, subtotal):
    """
    Validates coupon code against cart subtotal.
    Returns (is_valid, discount_amount, message, coupon_obj).
    """
    if not code:
        return False, Decimal('0.00'), "Coupon code is required.", None

    try:
        coupon = Coupon.objects.get(code__iexact=code.strip())
        is_valid, error_msg = coupon.is_valid(subtotal)
        if not is_valid:
            return False, Decimal('0.00'), error_msg, coupon

        discount = coupon.calculate_discount(subtotal)
        return True, discount, "Coupon applied successfully!", coupon
    except Coupon.DoesNotExist:
        return False, Decimal('0.00'), "Invalid coupon code.", None


def calculate_cart_totals(cart=None, coupon_code=None):
    """
    Calculates detailed pricing breakdown for a cart instance.
    """
    subtotal = Decimal('0.00')
    total_items = 0
    items_summary = []

    if cart:
        items = cart.items.select_related('product').filter(is_active=True)
        for item in items:
            unit_price = item.unit_price if item.unit_price is not None else item.product.selling_price
            line_total = unit_price * item.quantity
            subtotal += line_total
            total_items += item.quantity
            items_summary.append({
                'id': item.id,
                'product_id': item.product.id,
                'product_title': item.product.title,
                'product_slug': item.product.slug,
                'product_image': item.product.image.url if item.product.image else None,
                'quantity': item.quantity,
                'unit_price': unit_price,
                'total_price': line_total,
            })

    tax = round(Decimal('0.18') * subtotal, 2)

    coupon_discount = Decimal('0.00')
    coupon_message = ""
    coupon_obj = None
    if coupon_code:
        is_valid, coupon_discount, coupon_message, coupon_obj = apply_coupon_to_subtotal(coupon_code, subtotal)

    shipping_config = ShippingConfig.get_config()
    shipping_cost = shipping_config.get_shipping_cost(subtotal)

    grand_total = max(Decimal('0.00'), subtotal + tax - coupon_discount + shipping_cost)

    return {
        'cart_id': cart.id if cart else None,
        'subtotal': subtotal,
        'total_items': total_items,
        'tax': tax,
        'coupon_code': coupon_code if (coupon_obj and coupon_discount > 0) else None,
        'coupon_discount': coupon_discount,
        'coupon_message': coupon_message,
        'shipping_cost': shipping_cost,
        'free_shipping_threshold': shipping_config.free_shipping_threshold,
        'grand_total': grand_total,
        'items': items_summary,
    }


def build_order_from_cart(cart, address, payment_method='cod', coupon_code=None, user=None, session_key=None):
    """
    Creates snapshot Order & OrderItem models from active cart items.
    """
    totals = calculate_cart_totals(cart=cart, coupon_code=coupon_code)

    if totals['total_items'] == 0:
        raise ValueError("Cannot place an order with an empty cart.")

    order_number = Order.generate_order_number()

    order = Order.objects.create(
        order_number=order_number,
        user=user if (user and user.is_authenticated) else None,
        session_key=session_key if not (user and user.is_authenticated) else None,
        full_name=address.full_name,
        phone=address.phone,
        email=address.email or (user.email if user and user.is_authenticated else ''),
        address_line1=address.address_line1,
        address_line2=address.address_line2 or '',
        city=address.city,
        state=address.state,
        pincode=address.pincode,
        subtotal=totals['subtotal'],
        tax=totals['tax'],
        coupon_code=totals['coupon_code'],
        coupon_discount=totals['coupon_discount'],
        shipping_cost=totals['shipping_cost'],
        grand_total=totals['grand_total'],
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
    )

    # Create OrderItems
    items = cart.items.select_related('product').filter(is_active=True)
    for item in items:
        unit_price = item.unit_price if item.unit_price is not None else item.product.selling_price
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_title=item.product.title,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=unit_price * item.quantity,
        )

    # Increment coupon count if applied
    if totals['coupon_code']:
        Coupon.objects.filter(code=totals['coupon_code']).update(used_count=F('used_count') + 1)

    # Clear items from cart
    items.delete()

    return order
