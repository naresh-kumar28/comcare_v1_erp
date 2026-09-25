from urllib.parse import urlparse

from django.db.models import Q
from apps.cart.models import Cart, CartItem, Order, UserAddress
from apps.store.models import Wishlist


def safe_referer(request, default_url):
    """
    Return the request's Referer only when it is same-origin.

    Prevents open-redirect through an attacker-controlled HTTP_REFERER.
    """
    referer = request.META.get('HTTP_REFERER')
    if not referer:
        return default_url
    try:
        referer_parts = urlparse(referer)
        origin_parts = urlparse(request.build_absolute_uri('/'))
    except ValueError:
        return default_url
    if referer_parts.netloc != origin_parts.netloc:
        return default_url
    return referer


def link_guest_orders(user):
    """
    Links past guest orders (where order.user is NULL) matching the user's email or phone_number
    to this user account upon login or registration.
    """
    if not user or not user.is_authenticated:
        return 0

    query_conditions = Q()

    if getattr(user, 'email', None) and user.email.strip():
        query_conditions |= Q(email__iexact=user.email.strip())

    phone = getattr(user, 'phone_number', None)
    if phone and str(phone).strip():
        clean_phone = str(phone).strip()
        query_conditions |= Q(phone=clean_phone)
        if clean_phone.startswith('+91'):
            query_conditions |= Q(phone=clean_phone[3:])
        elif len(clean_phone) == 10:
            query_conditions |= Q(phone=f"+91{clean_phone}")

    if not query_conditions:
        return 0

    unlinked_orders = Order.objects.filter(user__isnull=True).filter(query_conditions)
    count = unlinked_orders.count()
    if count > 0:
        unlinked_orders.update(user=user)
    return count


def link_guest_addresses(user, old_session_key=None):
    """
    Links past unlinked guest UserAddress records to the authenticated user account upon login/registration.
    Checks matching by guest session_key, email, or phone_number.
    """
    if not user or not user.is_authenticated:
        return 0

    linked_count = 0

    if old_session_key:
        session_addresses = UserAddress.objects.filter(session_key=old_session_key, user__isnull=True)
        linked_count += session_addresses.update(user=user, session_key=None)

    query_conditions = Q()
    if getattr(user, 'email', None) and user.email.strip():
        query_conditions |= Q(email__iexact=user.email.strip())

    phone = getattr(user, 'phone_number', None)
    if phone and str(phone).strip():
        clean_phone = str(phone).strip()
        query_conditions |= Q(phone=clean_phone)
        if clean_phone.startswith('+91'):
            query_conditions |= Q(phone=clean_phone[3:])
        elif len(clean_phone) == 10:
            query_conditions |= Q(phone=f"+91{clean_phone}")

    if query_conditions:
        unlinked_by_contact = UserAddress.objects.filter(user__isnull=True).filter(query_conditions)
        linked_count += unlinked_by_contact.update(user=user, session_key=None)

    return linked_count


def merge_guest_cart_and_wishlist(user, old_session_key, new_session_key=None):
    """
    Transfers/merges guest cart items and guest wishlist items to the authenticated user account upon login/registration.
    Adds quantities for duplicate cart products and prevents duplicate wishlist items.
    """
    if not user or not user.is_authenticated:
        return

    # 1. Merge Guest Cart -> User Cart
    try:
        user_cart = Cart.objects.filter(user=user, is_active=True).first()
        if not user_cart:
            user_cart = Cart.objects.create(
                user=user,
                is_active=True,
                session_key=new_session_key or old_session_key
            )

        keys_to_check = list(set([k for k in [old_session_key, new_session_key] if k]))
        if keys_to_check:
            guest_carts = Cart.objects.filter(session_key__in=keys_to_check, is_active=True).exclude(pk=user_cart.pk)
            for guest_cart in guest_carts:
                for item in guest_cart.items.all():
                    user_item, created = CartItem.objects.get_or_create(
                        cart=user_cart,
                        product=item.product,
                        defaults={'quantity': item.quantity, 'unit_price': item.unit_price}
                    )
                    if not created:
                        user_item.quantity += item.quantity
                        user_item.save()
                guest_cart.delete()

        user_cart.user = user
        if new_session_key:
            user_cart.session_key = new_session_key
        user_cart.save()
    except Exception as e:
        print(f"Error merging guest cart: {e}")

    # 2. Merge Guest Wishlist -> User Wishlist
    try:
        keys_to_check = list(set([k for k in [old_session_key, new_session_key] if k]))
        if keys_to_check:
            guest_wishlist_items = Wishlist.objects.filter(session_key__in=keys_to_check, user__isnull=True)
            for g_item in guest_wishlist_items:
                if not Wishlist.objects.filter(user=user, product=g_item.product).exists():
                    g_item.user = user
                    g_item.session_key = None
                    g_item.save()
                else:
                    g_item.delete()
    except Exception as e:
        print(f"Error merging guest wishlist: {e}")
