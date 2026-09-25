from decimal import Decimal
import json
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from apps.store.models import Product
from .models import Cart, CartItem, Order, OrderItem, ShippingConfig, UserAddress


def _cart_id(request):
    # NOTE: request.session.create() returns None; never reassign it.
    # Return the existing key or create a session and return the new key.
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def _get_user_cart(request, create=False):
    session_key = _cart_id(request)
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(Q(user=request.user) | Q(session_key=session_key)).order_by('-updated_at').first()
        if cart:
            updated = False
            if cart.user is None:
                cart.user = request.user
                updated = True
            if cart.session_key != session_key:
                cart.session_key = session_key
                updated = True
            if updated:
                cart.save()
        elif create:
            cart = Cart.objects.create(user=request.user, session_key=session_key)
    else:
        cart = Cart.objects.filter(session_key=session_key).order_by('-updated_at').first()
        if not cart and create:
            cart = Cart.objects.create(session_key=session_key)

    return cart


def _clear_cart(request, is_buy_now=False, bought_product_ids=None):
    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    if user:
        carts = Cart.objects.filter(Q(user=user) | Q(session_key=session_key))
    else:
        carts = Cart.objects.filter(session_key=session_key)

    if is_buy_now and bought_product_ids:
        CartItem.objects.filter(cart__in=carts, product_id__in=bought_product_ids).delete()
    else:
        CartItem.objects.filter(cart__in=carts).delete()

    if 'coupon_code' in request.session:
        del request.session['coupon_code']
    if 'buy_now_item' in request.session:
        del request.session['buy_now_item']
    request.session.modified = True


def _get_cart_context(request):
    total = Decimal('0.00')
    quantity = 0
    cart_items = []
    coupon_code = ''
    coupon_discount = Decimal('0.00')
    coupon_error = ''
    coupon_obj = None

    cart = _get_user_cart(request, create=False)
    if cart:
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            line_price = cart_item.unit_price if cart_item.unit_price is not None else cart_item.product.selling_price
            total += (line_price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (Decimal('0.18') * total)

        # --- Coupon logic ---
        session_code = request.session.get('coupon_code', '')
        if session_code:
            from apps.coupons.models import Coupon
            try:
                coupon_obj = Coupon.objects.get(code=session_code)
                is_valid, error_msg = coupon_obj.is_valid(total)
                if is_valid:
                    coupon_code = coupon_obj.code
                    coupon_discount = coupon_obj.calculate_discount(total)
                else:
                    coupon_error = error_msg
                    del request.session['coupon_code']
                    request.session.modified = True
            except Coupon.DoesNotExist:
                del request.session['coupon_code']
                request.session.modified = True

        # --- Shipping logic ---
        shipping_config = ShippingConfig.get_config()
        shipping_cost = shipping_config.get_shipping_cost(total)
        free_shipping_threshold = shipping_config.free_shipping_threshold

        grand_total = total + tax - coupon_discount + shipping_cost
    else:
        tax = Decimal('0.00')
        shipping_cost = Decimal('0.00')
        free_shipping_threshold = Decimal('0.00')
        grand_total = Decimal('0.00')

    return {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'coupon_error': coupon_error,
        'coupon_obj': coupon_obj,
        'shipping_cost': shipping_cost,
        'free_shipping_threshold': free_shipping_threshold,
        'grand_total': grand_total,
        'is_buy_now': False,
    }


def _get_buy_now_context(request):
    buy_now_data = request.session.get('buy_now_item')
    if not buy_now_data:
        return None

    product = Product.objects.filter(id=buy_now_data.get('product_id'), is_active=True).first()
    if not product:
        return None

    try:
        quantity = int(buy_now_data.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    unit_price = product.selling_price
    total = unit_price * quantity
    tax = (Decimal('0.18') * total)

    class MockCartItem:
        def __init__(self, product, quantity, unit_price):
            self.product = product
            self.quantity = quantity
            self.unit_price = unit_price
            self.total_price = unit_price * quantity

    mock_item = MockCartItem(product, quantity, unit_price)

    # Coupon logic
    coupon_code = ''
    coupon_discount = Decimal('0.00')
    coupon_error = ''
    coupon_obj = None

    session_code = request.session.get('coupon_code', '')
    if session_code:
        from apps.coupons.models import Coupon
        try:
            coupon_obj = Coupon.objects.get(code=session_code)
            is_valid, error_msg = coupon_obj.is_valid(total)
            if is_valid:
                coupon_code = coupon_obj.code
                coupon_discount = coupon_obj.calculate_discount(total)
            else:
                coupon_error = error_msg
                del request.session['coupon_code']
                request.session.modified = True
        except Coupon.DoesNotExist:
            del request.session['coupon_code']
            request.session.modified = True

    # Shipping logic
    shipping_config = ShippingConfig.get_config()
    shipping_cost = shipping_config.get_shipping_cost(total)
    free_shipping_threshold = shipping_config.free_shipping_threshold

    grand_total = total + tax - coupon_discount + shipping_cost

    return {
        'total': total,
        'quantity': quantity,
        'cart_items': [mock_item],
        'tax': tax,
        'coupon_code': coupon_code,
        'coupon_discount': coupon_discount,
        'coupon_error': coupon_error,
        'coupon_obj': coupon_obj,
        'shipping_cost': shipping_cost,
        'free_shipping_threshold': free_shipping_threshold,
        'grand_total': grand_total,
        'is_buy_now': True,
        'buy_now_product_id': product.id,
        'buy_now_quantity': quantity,
    }


def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    try:
        quantity = int(request.GET.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except ValueError:
        quantity = 1

    # Store isolated buy_now_item in session
    request.session['buy_now_item'] = {
        'product_id': product.id,
        'quantity': quantity,
    }
    request.session.modified = True

    return redirect(f"{reverse('checkout')}?buy_now=1")


def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_user_cart(request, create=True)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': 1,
            'unit_price': product.selling_price,
            'is_active': True,
        },
    )
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('HX-Request'):
        context = _get_cart_context(request)
        return render(request, 'partials/cart_container.html', context)
    return redirect('cart')


def remove_cart(request, product_id):
    cart = _get_user_cart(request, create=False)
    product = get_object_or_404(Product, id=product_id)

    if cart:
        cart_item = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()

    if request.headers.get('HX-Request'):
        context = _get_cart_context(request)
        return render(request, 'partials/cart_container.html', context)
    return redirect('cart')


def remove_cart_item(request, product_id):
    cart = _get_user_cart(request, create=False)
    product = get_object_or_404(Product, id=product_id)

    if cart:
        CartItem.objects.filter(cart=cart, product=product).delete()

    if request.headers.get('HX-Request'):
        context = _get_cart_context(request)
        return render(request, 'partials/cart_container.html', context)
    return redirect('cart')


def cart(request):
    context = _get_cart_context(request)
    return render(request, 'cart.html', context)


def add_cart_ajax(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    cart = _get_user_cart(request, create=True)

    try:
        qty = int(request.GET.get('quantity', 1))
    except ValueError:
        qty = 1

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': qty,
            'unit_price': product.selling_price,
            'is_active': True,
        },
    )
    if not created:
        cart_item.quantity += qty
        cart_item.save()

    cart_count = 0
    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
    for item in cart_items:
        cart_count += item.quantity

    view_type = request.GET.get('view', 'detail')
    context = {
        'product': product,
        'cart_count': cart_count,
        'quantity': qty,
    }

    if view_type == 'card':
        return render(request, 'partials/ajax_add_card_response.html', context)
    else:
        return render(request, 'partials/ajax_add_detail_response.html', context)


def checkout(request):
    is_buy_now = request.GET.get('buy_now') == '1' or 'buy_now_item' in request.session
    if is_buy_now:
        cart_context = _get_buy_now_context(request)
        if not cart_context:
            request.session.pop('buy_now_item', None)
            return redirect('cart')
    else:
        cart_context = _get_cart_context(request)
        if not cart_context['cart_items']:
            return redirect('cart')

    session_key = _cart_id(request)

    # User addresses
    if request.user.is_authenticated:
        addresses = UserAddress.objects.filter(user=request.user).order_by('id')
    else:
        addresses = UserAddress.objects.filter(session_key=session_key).order_by('id')

    context = {
        **cart_context,
        'addresses': addresses,
        'razorpay_key_id': getattr(settings, 'RAZORPAY_KEY_ID', ''),
    }
    return render(request, 'checkout.html', context)


@require_POST
def save_address(request):
    address_id = request.POST.get('address_id')
    full_name = request.POST.get('full_name', '').strip()
    phone = request.POST.get('phone', '').strip()
    email = request.POST.get('email', '').strip()
    address_line1 = request.POST.get('address_line1', '').strip()
    address_line2 = request.POST.get('address_line2', '').strip()
    city = request.POST.get('city', 'Purnea').strip()
    state = request.POST.get('state', 'Bihar').strip()
    pincode = request.POST.get('pincode', '').strip()
    address_type = request.POST.get('address_type', 'home').strip()
    is_default = request.POST.get('is_default') == 'true' or request.POST.get('is_default') == 'on' or request.POST.get('is_default') == '1'

    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    if not email and user and user.email:
        email = user.email

    if is_default:
        if user:
            UserAddress.objects.filter(user=user).update(is_default=False)
        else:
            UserAddress.objects.filter(session_key=session_key).update(is_default=False)

    if address_id:
        if user:
            address = get_object_or_404(UserAddress, id=address_id, user=user)
        else:
            address = get_object_or_404(UserAddress, id=address_id, session_key=session_key)
    else:
        existing_qs = UserAddress.objects.filter(user=user) if user else UserAddress.objects.filter(session_key=session_key)
        if existing_qs.count() == 0:
            is_default = True

        address = UserAddress(
            user=user,
            session_key=session_key if not user else None,
        )

    address.full_name = full_name
    address.phone = phone
    address.email = email
    address.address_line1 = address_line1
    address.address_line2 = address_line2
    address.city = city
    address.state = state
    address.pincode = pincode
    address.address_type = address_type
    address.is_default = is_default
    address.save()

    if user:
        addresses = UserAddress.objects.filter(user=user).order_by('id')
    else:
        addresses = UserAddress.objects.filter(session_key=session_key).order_by('id')

    view_type = request.POST.get('view_type') or request.GET.get('view_type', 'grid')
    template = 'partials/checkout_address_list.html' if view_type == 'checkout' else 'partials/address_grid.html'

    response = render(request, template, {'addresses': addresses})
    response['X-New-Address-Id'] = str(address.id)
    return response


def get_address_json(request, address_id):
    session_key = _cart_id(request)
    if request.user.is_authenticated:
        address = get_object_or_404(UserAddress, id=address_id, user=request.user)
    else:
        address = get_object_or_404(UserAddress, id=address_id, session_key=session_key)

    return JsonResponse({
        'id': address.id,
        'full_name': address.full_name,
        'phone': address.phone,
        'email': address.email or '',
        'address_line1': address.address_line1,
        'address_line2': address.address_line2 or '',
        'city': address.city,
        'state': address.state,
        'pincode': address.pincode,
        'address_type': address.address_type,
        'is_default': address.is_default,
    })


@require_POST
def set_default_address(request, address_id):
    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    if user:
        UserAddress.objects.filter(user=user).update(is_default=False)
        address = get_object_or_404(UserAddress, id=address_id, user=user)
    else:
        UserAddress.objects.filter(session_key=session_key).update(is_default=False)
        address = get_object_or_404(UserAddress, id=address_id, session_key=session_key)

    address.is_default = True
    address.save()

    if user:
        addresses = UserAddress.objects.filter(user=user).order_by('id')
    else:
        addresses = UserAddress.objects.filter(session_key=session_key).order_by('id')

    view_type = request.POST.get('view_type') or request.GET.get('view_type', 'grid')
    template = 'partials/checkout_address_list.html' if view_type == 'checkout' else 'partials/address_grid.html'
    return render(request, template, {'addresses': addresses})


@require_POST
def delete_address(request, address_id):
    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    if user:
        address = get_object_or_404(UserAddress, id=address_id, user=user)
    else:
        address = get_object_or_404(UserAddress, id=address_id, session_key=session_key)

    was_default = address.is_default
    address.delete()

    if user:
        addresses = UserAddress.objects.filter(user=user).order_by('id')
    else:
        addresses = UserAddress.objects.filter(session_key=session_key).order_by('id')

    if was_default and addresses.exists():
        first_addr = addresses.first()
        first_addr.is_default = True
        first_addr.save()

    view_type = request.POST.get('view_type') or request.GET.get('view_type', 'grid')
    template = 'partials/checkout_address_list.html' if view_type == 'checkout' else 'partials/address_grid.html'
    return render(request, template, {'addresses': addresses})


@require_POST
def place_order(request):
    is_buy_now = request.POST.get('is_buy_now') == '1' or 'buy_now_item' in request.session

    if is_buy_now:
        cart_context = _get_buy_now_context(request)
    else:
        cart_context = _get_cart_context(request)

    if not cart_context or not cart_context.get('cart_items'):
        return JsonResponse({'status': 'error', 'message': 'No products found to checkout!'}, status=400)

    cart_items = cart_context['cart_items']
    address_id = request.POST.get('address_id')
    payment_method = request.POST.get('payment_method', 'cod')

    session_key = _cart_id(request)
    user = request.user if request.user.is_authenticated else None

    # Fetch address
    address = None
    if address_id:
        if user:
            address = UserAddress.objects.filter(id=address_id, user=user).first()
        else:
            address = UserAddress.objects.filter(id=address_id, session_key=session_key).first()

    if not address:
        if user:
            address = UserAddress.objects.filter(user=user).first()
        else:
            address = UserAddress.objects.filter(session_key=session_key).first()

    if not address:
        full_name = request.POST.get('full_name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address_line1 = request.POST.get('address_line1', '').strip()
        pincode = request.POST.get('pincode', '').strip()
        if full_name and phone and address_line1 and pincode:
            address = UserAddress.objects.create(
                user=user,
                session_key=session_key if not user else None,
                full_name=full_name,
                phone=phone,
                email=request.POST.get('email', ''),
                address_line1=address_line1,
                address_line2=request.POST.get('address_line2', ''),
                city=request.POST.get('city', 'Purnea'),
                state=request.POST.get('state', 'Bihar'),
                pincode=pincode,
                is_default=True,
            )
        else:
            return JsonResponse({'status': 'error', 'message': 'Please add a valid delivery address!'}, status=400)

    # Create Order
    order_number = Order.generate_order_number()
    order = Order.objects.create(
        order_number=order_number,
        user=user,
        session_key=session_key if not user else None,
        full_name=address.full_name,
        phone=address.phone,
        email=address.email or (user.email if user else ''),
        address_line1=address.address_line1,
        address_line2=address.address_line2 or '',
        city=address.city,
        state=address.state,
        pincode=address.pincode,
        subtotal=cart_context['total'],
        tax=cart_context['tax'],
        coupon_code=cart_context['coupon_code'],
        coupon_discount=cart_context['coupon_discount'],
        shipping_cost=cart_context['shipping_cost'],
        grand_total=cart_context['grand_total'],
        payment_method=payment_method,
        payment_status='pending',
        order_status='pending',
    )

    # Increment Coupon used_count if a coupon was applied to this order
    if cart_context.get('coupon_code'):
        from apps.coupons.models import Coupon
        from django.db.models import F
        Coupon.objects.filter(code=cart_context['coupon_code']).update(used_count=F('used_count') + 1)

    # Create Order Items
    for item in cart_items:
        unit_price = item.unit_price if item.unit_price is not None else item.product.selling_price
        OrderItem.objects.create(
            order=order,
            product=item.product,
            product_title=item.product.title,
            quantity=item.quantity,
            unit_price=unit_price,
            total_price=unit_price * item.quantity,
        )

    # Store flag in session to prevent cart deletion on payment verification if buy_now
    if is_buy_now:
        request.session['order_is_buy_now_' + order_number] = True

    if payment_method == 'razorpay':
        key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')

        if key_id and key_secret:
            import razorpay
            client = razorpay.Client(auth=(key_id, key_secret))
            amount_paise = int(order.grand_total * 100)
            razorpay_order = client.order.create({
                'amount': amount_paise,
                'currency': 'INR',
                'payment_capture': '1',
                'notes': {
                    'order_number': order.order_number
                }
            })
            order.razorpay_order_id = razorpay_order['id']
            order.save()

            return JsonResponse({
                'status': 'razorpay',
                'key_id': key_id,
                'amount': amount_paise,
                'currency': 'INR',
                'order_id': razorpay_order['id'],
                'order_number': order.order_number,
                'name': 'ComCare',
                'description': f"Order #{order.order_number}",
                'prefill_name': order.full_name,
                'prefill_email': order.email or '',
                'prefill_contact': order.phone,
            })
        else:
            order.payment_status = 'pending'
            order.save()

    # Clear buy_now_item session or clear Cart if normal checkout
    bought_product_ids = [item.product.id for item in cart_items]
    _clear_cart(request, is_buy_now=is_buy_now, bought_product_ids=bought_product_ids)

    return JsonResponse({
        'status': 'success',
        'redirect_url': f'/cart/order-success/?order_number={order.order_number}'
    })


def _can_access_order(request, order):
    """Return True only for the order's owner or staff.

    Used to avoid leaking order details / PII through guessable order numbers.
    """
    user = request.user
    if user.is_authenticated and user.is_staff:
        return True
    if user.is_authenticated and order.user and order.user_id == user.id:
        return True
    if user.is_authenticated and order.user is None and order.email:
        if order.email.lower() == getattr(user, 'email', '').lower():
            return True
    if order.session_key and order.session_key == request.session.session_key:
        return True
    return False


@require_POST
def verify_payment(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    razorpay_order_id = data.get('razorpay_order_id') or ''
    razorpay_payment_id = data.get('razorpay_payment_id') or ''
    razorpay_signature = data.get('razorpay_signature') or ''
    order_number = data.get('order_number')

    order = get_object_or_404(Order, order_number=order_number)

    # Idempotency: a successfully paid order is never processed twice.
    if order.payment_status == 'paid':
        return JsonResponse({
            'status': 'success',
            'redirect_url': f'/cart/order-success/?order_number={order.order_number}'
        })

    key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')

    verified = False
    if key_id and key_secret:
        # The signature must belong to the Razorpay order id that the server
        # itself created for THIS order at placement time. This prevents
        # replaying a payment made against a different (cheaper) order.
        if not order.razorpay_order_id or razorpay_order_id != order.razorpay_order_id:
            verified = False
        else:
            import razorpay
            client = razorpay.Client(auth=(key_id, key_secret))
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': razorpay_order_id,
                    'razorpay_payment_id': razorpay_payment_id,
                    'razorpay_signature': razorpay_signature
                })
                verified = True
            except razorpay.errors.SignatureVerificationError:
                verified = False
    elif settings.DEBUG:
        # Local development sandbox only (signatureless test flow).
        # NEVER active in production: in production missing keys must fail.
        verified = True
    else:
        verified = False

    if verified:
        order.payment_status = 'paid'
        order.order_status = 'processing'
        if razorpay_payment_id:
            order.razorpay_payment_id = razorpay_payment_id
        if razorpay_signature:
            order.razorpay_signature = razorpay_signature
        order.save()

        is_buy_now = request.session.pop('order_is_buy_now_' + order_number, False)
        order_items_product_ids = list(order.items.values_list('product_id', flat=True))
        _clear_cart(request, is_buy_now=is_buy_now, bought_product_ids=order_items_product_ids)

        return JsonResponse({
            'status': 'success',
            'redirect_url': f'/cart/order-success/?order_number={order.order_number}'
        })

    if order.payment_status != 'paid':
        order.payment_status = 'failed'
        order.save()
    return JsonResponse({'status': 'error', 'message': 'Payment verification failed!'}, status=400)


def order_success(request):
    order_number = request.GET.get('order_number')
    order = None
    if order_number:
        order = Order.objects.filter(order_number=order_number).first()
        if order and not _can_access_order(request, order):
            order = None

    context = {
        'order': order,
    }
    return render(request, 'order_success.html', context)