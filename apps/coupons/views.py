from django.shortcuts import render

from apps.cart.views import _get_cart_context


def apply_coupon(request):
    """Validate & apply coupon code from POST, re-render cart container."""
    from apps.coupons.models import Coupon

    code = request.POST.get('coupon_code', '').strip().upper()

    if not code:
        context = _get_cart_context(request)
        context['coupon_error'] = 'Please enter a coupon code.'
        return render(request, 'partials/cart_container.html', context)

    try:
        coupon = Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        context = _get_cart_context(request)
        context['coupon_error'] = 'Invalid coupon code. Please try again.'
        return render(request, 'partials/cart_container.html', context)

    # Get subtotal for validation
    context = _get_cart_context(request)
    subtotal = context['total']

    is_valid, error_msg = coupon.is_valid(subtotal)
    if not is_valid:
        context['coupon_error'] = error_msg
        return render(request, 'partials/cart_container.html', context)

    # Store coupon in session
    request.session['coupon_code'] = coupon.code

    # Re-build context with coupon applied
    context = _get_cart_context(request)
    return render(request, 'partials/cart_container.html', context)


def remove_coupon(request):
    """Remove applied coupon from session and re-render cart container."""
    if 'coupon_code' in request.session:
        del request.session['coupon_code']
        request.session.modified = True

    context = _get_cart_context(request)
    return render(request, 'partials/cart_container.html', context)
