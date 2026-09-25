from django.db.models import Q
from .models import Cart, CartItem
from .views import _cart_id
from apps.store.models import Wishlist

def cart_counter(request):
    cart_count = 0
    if request.path.startswith('/admin'):
        return {}
    cart_product_ids = []
    session_key = _cart_id(request)

    try:
        if request.user.is_authenticated:
            cart = Cart.objects.filter(Q(user=request.user) | Q(session_key=session_key)).order_by('-updated_at').first()
        else:
            cart = Cart.objects.filter(session_key=session_key).order_by('-updated_at').first()

        if cart:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
            for item in cart_items:
                cart_count += item.quantity
                cart_product_ids.append(item.product.id)
    except Exception:
        pass

    user_wishlist_ids = []
    if request.user.is_authenticated:
        user_wishlist_ids = list(Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True))
    else:
        user_wishlist_ids = list(Wishlist.objects.filter(session_key=session_key, user__isnull=True).values_list('product_id', flat=True))
    
    wishlist_count = len(user_wishlist_ids)

    return {
        'cart_count': cart_count,
        'cart_product_ids': cart_product_ids,
        'wishlist_count': wishlist_count,
        'user_wishlist_ids': user_wishlist_ids,
    }
