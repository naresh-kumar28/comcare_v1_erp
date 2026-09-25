from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from apps.cart.utils import link_guest_orders, link_guest_addresses, merge_guest_cart_and_wishlist


@receiver(user_logged_in)
def handle_user_login(sender, request, user, **kwargs):
    """
    Signal handler triggered on every user login or registration.
    1. Links past guest orders matching user's email or phone_number to user account.
    2. Links past guest UserAddress records to user account.
    3. Merges guest session cart and wishlist items into user account.
    """
    if not user or not user.is_authenticated:
        return

    # 1. Link guest orders
    try:
        link_guest_orders(user)
    except Exception as e:
        print(f"Error linking guest orders on login: {e}")

    # 2. Link guest addresses & merge cart/wishlist
    if request:
        try:
            old_session_key = getattr(request, '_pre_login_session_key', None) or request.session.get('guest_session_key')
            new_session_key = getattr(request.session, 'session_key', None)

            link_guest_addresses(user, old_session_key)
            merge_guest_cart_and_wishlist(user, old_session_key, new_session_key)

            if hasattr(request, 'session'):
                request.session.pop('guest_session_key', None)
        except Exception as e:
            print(f"Error linking addresses or merging cart/wishlist on login: {e}")
