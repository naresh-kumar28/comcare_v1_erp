import time
from decimal import Decimal
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q
from django.http import JsonResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, TemplateView

from apps.accounts.forms import UserRegisterForm
from apps.accounts.models import CustomUser
from apps.cart.models import Cart, CartItem, Order, UserAddress
from apps.cart.utils import merge_guest_cart_and_wishlist, safe_referer
from apps.cart.views import _cart_id
from apps.services.models import ServiceRequest
from apps.store.models import Product, Wishlist


# --- Helper Function for SPA / Partial Dashboard Rendering ---

def render_account_page(request, template_name, context=None):
    """
    Renders account pages dynamically. If the request is an HTMX navigation request
    targeting '#account-main-content', returns the partial base template for smooth SPA switching.
    """
    context = context or {}
    hx_target = request.headers.get('HX-Target', '')
    if request.headers.get('HX-Request') and (not hx_target or hx_target in ['account-main-content', '#account-main-content']):
        time.sleep(0.18)  # Perception delay for smooth skeleton loader animation
        context['base_template'] = 'partials/account_partial_base.html'
    else:
        context['base_template'] = 'account_base.html'
    return render(request, template_name, context)


# --- Class-Based Authentication & Account Views ---

class UserRegisterView(SuccessMessageMixin, CreateView):
    """
    User Registration View using Django's built-in CreateView and UserRegisterForm (UserCreationForm).
    """
    form_class = UserRegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('dashboard')
    success_message = "Account created successfully! Welcome to ComCare."

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        old_session_key = _cart_id(self.request)
        response = super().form_valid(form)
        
        # Log in the newly registered user
        auth_login(self.request, self.object)
        
        # Merge guest cart and wishlist
        new_session_key = self.request.session.session_key
        merge_guest_cart_and_wishlist(self.object, old_session_key, new_session_key)
        
        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    """
    Account Dashboard View displaying user statistics, recent orders, and quick links.
    """
    login_url = 'login'
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        user = request.user
        full_name = user.get_full_name().strip()
        user_name = full_name if full_name else (user.first_name or user.email.split('@')[0].title())
        initials = "".join([part[0].upper() for part in user_name.split()[:2]]) if user_name else "U"

        user_orders = Order.objects.filter(user=user)
        total_orders = user_orders.count()
        recent_orders_qs = user_orders.order_by('-created_at')[:5]

        recent_orders = []
        for order in recent_orders_qs:
            first_item = order.items.first()
            item_title = first_item.product.title if first_item and first_item.product else "Order Package"
            item_image_url = first_item.product.image.url if (first_item and first_item.product and first_item.product.image) else None
            status_display = order.get_order_status_display()

            if order.order_status == 'delivered':
                status_class = 'bg-emerald-50 text-emerald-700 border-emerald-200'
            elif order.order_status == 'shipped':
                status_class = 'bg-indigo-50 text-indigo-700 border-indigo-200'
            elif order.order_status == 'processing':
                status_class = 'bg-blue-50 text-[var(--color-primary)] border-blue-200'
            elif order.order_status == 'pending':
                status_class = 'bg-amber-50 text-amber-700 border-amber-200'
            elif order.order_status == 'cancelled':
                status_class = 'bg-red-50 text-red-700 border-red-200'
            else:
                status_class = 'bg-gray-50 text-gray-700 border-gray-200'

            recent_orders.append({
                'order_number': order.order_number,
                'item_title': item_title,
                'item_image_url': item_image_url,
                'grand_total': order.grand_total,
                'created_at': order.created_at,
                'order_status': order.order_status,
                'status_display': status_display,
                'status_class': status_class,
            })

        active_qs = ServiceRequest.objects.exclude(status__in=['completed', 'cancelled'])
        if user.is_staff or user.is_superuser:
            active_repairs = active_qs.count()
        else:
            query = Q(user=user)
            user_phone = getattr(user, 'phone_number', None)
            if user_phone:
                query |= Q(phone=user_phone)
            active_repairs = active_qs.filter(query).count()

        saved_addresses_count = UserAddress.objects.filter(user=user).count()
        wishlist_count = Wishlist.objects.filter(user=user).count()

        context = {
            'user_name': user_name,
            'user_initials': initials,
            'total_orders': total_orders,
            'active_repairs': active_repairs,
            'wishlist_count': wishlist_count,
            'saved_addresses_count': saved_addresses_count,
            'recent_orders': recent_orders,
        }
        return render_account_page(request, self.template_name, context)


class AccountOrdersView(LoginRequiredMixin, TemplateView):
    """
    Order History View listing all orders placed by the user with HTMX Infinite Scroll support.
    """
    login_url = 'login'
    template_name = 'orders.html'

    def get(self, request, *args, **kwargs):
        orders_qs = Order.objects.filter(user=request.user).prefetch_related('items__product').order_by('-created_at')

        from django.core.paginator import Paginator
        paginator = Paginator(orders_qs, 4)  # 4 orders per page for infinite scroll
        page_number = request.GET.get('page', 1)
        orders_page = paginator.get_page(page_number)

        orders_data = []
        for order in orders_page:
            if order.order_status == 'delivered':
                status_class = 'bg-emerald-50 text-emerald-700 border-emerald-200'
            elif order.order_status in ['processing', 'shipped']:
                status_class = 'bg-blue-50 text-[var(--color-primary)] border-blue-200'
            elif order.order_status == 'pending':
                status_class = 'bg-amber-50 text-amber-700 border-amber-200'
            elif order.order_status == 'cancelled':
                status_class = 'bg-red-50 text-red-700 border-red-200'
            else:
                status_class = 'bg-gray-50 text-gray-700 border-gray-200'

            items = []
            for item in order.items.all():
                items.append({
                    'title': item.product.title if item.product else 'Product Item',
                    'quantity': item.quantity,
                    'unit_price': item.unit_price if item.unit_price is not None else (item.product.selling_price if item.product else 0),
                    'total_price': item.total_price if hasattr(item, 'total_price') else (item.unit_price * item.quantity if item.unit_price else 0),
                    'image_url': item.product.image.url if (item.product and item.product.image) else None,
                })

            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'created_at': order.created_at,
                'payment_method_display': order.get_payment_method_display(),
                'payment_status_display': order.get_payment_status_display(),
                'order_status': order.order_status,
                'status_display': order.get_order_status_display(),
                'status_class': status_class,
                'grand_total': order.grand_total,
                'address_summary': f"{order.address_line1}, {order.city}" if order.address_line1 else order.city,
                'can_cancel': order.order_status in ['pending', 'processing'],
                'can_return': order.order_status == 'delivered',
                'items': items,
            })

        context = {
            'orders': orders_data,
            'orders_page': orders_page,
            'orders_count': paginator.count,
        }

        if request.headers.get('HX-Request') and request.GET.get('page'):
            return render(request, 'partials/order_cards.html', context)

        return render_account_page(request, self.template_name, context)


class CancelOrderView(LoginRequiredMixin, View):
    """
    Cancel Order View to process order cancellation requests.
    """
    login_url = 'login'

    def post(self, request, order_id=None):
        target_id = order_id or request.POST.get('order_id')
        if target_id:
            try:
                target_str = str(target_id).strip()
                if target_str.isdigit():
                    order = Order.objects.get(id=int(target_str), user=request.user)
                else:
                    order = Order.objects.get(order_number=target_str, user=request.user)

                if order.order_status in ['pending', 'processing']:
                    order.order_status = 'cancelled'
                    order.save()
                    messages.success(request, f"Order #{order.order_number} has been cancelled successfully.")
                else:
                    messages.error(request, f"Order #{order.order_number} cannot be cancelled as it is already {order.get_order_status_display()}.")
            except Order.DoesNotExist:
                messages.error(request, "Order not found or access denied.")
            except Exception as e:
                messages.error(request, f"Could not cancel order: {str(e)}")
        return redirect('account_orders')


# Standard Configurable GST Settings
DEFAULT_GST_RATE = Decimal('18.0')
SELLER_STATE = "BIHAR"
SELLER_STATE_CODE = "10"

INDIAN_STATE_CODES = {
    'JAMMU & KASHMIR': '01', 'JAMMU AND KASHMIR': '01', 'JK': '01',
    'HIMACHAL PRADESH': '02', 'HP': '02',
    'PUNJAB': '03', 'PB': '03',
    'CHANDIGARH': '04', 'CH': '04',
    'UTTARAKHAND': '05', 'UTTARANCHAL': '05', 'UK': '05',
    'HARYANA': '06', 'HR': '06',
    'DELHI': '07', 'DL': '07',
    'RAJASTHAN': '08', 'RJ': '08',
    'UTTAR PRADESH': '09', 'UP': '09',
    'BIHAR': '10', 'BR': '10',
    'SIKKIM': '11', 'SK': '11',
    'ARUNACHAL PRADESH': '12', 'AR': '12',
    'NAGALAND': '13', 'NL': '13',
    'MANIPUR': '14', 'MN': '14',
    'MIZORAM': '15', 'MZ': '15',
    'TRIPURA': '16', 'TR': '16',
    'MEGHALAYA': '17', 'ML': '17',
    'ASSAM': '18', 'AS': '18',
    'WEST BENGAL': '19', 'WB': '19',
    'JHARKHAND': '20', 'JH': '20',
    'ODISHA': '21', 'ORISSA': '21', 'OR': '21', 'OD': '21',
    'CHHATTISGARH': '22', 'CG': '22',
    'MADHYA PRADESH': '23', 'MP': '23',
    'GUJARAT': '24', 'GJ': '24',
    'DAMAN AND DIU': '25',
    'DADRA AND NAGAR HAVELI': '26',
    'MAHARASHTRA': '27', 'MH': '27',
    'ANDHRA PRADESH': '28', 'AP': '28',
    'KARNATAKA': '29', 'KA': '29',
    'GOA': '30', 'GA': '30',
    'LAKSHADWEEP': '31',
    'KERALA': '32', 'KL': '32',
    'TAMIL NADU': '33', 'TN': '33',
    'PUDUCHERRY': '34', 'PONDICHERRY': '34', 'PY': '34',
    'ANDAMAN AND NICOBAR ISLANDS': '35',
    'TELANGANA': '36', 'TS': '36',
    'LADAKH': '38'
}


def build_invoice_context(order):
    """
    Constructs GST-compliant tax calculations and context dictionary for rendering invoice.html.
    """
    buyer_state_raw = (order.state or '').strip()
    buyer_state_upper = buyer_state_raw.upper()
    buyer_state_code = INDIAN_STATE_CODES.get(buyer_state_upper, SELLER_STATE_CODE)
    place_of_supply = f"{buyer_state_code} - {buyer_state_raw if buyer_state_raw else 'Bihar'}"

    gst_rate = getattr(settings, 'INVOICE_GST_RATE', DEFAULT_GST_RATE)
    total_tax = order.tax if (order.tax and order.tax > Decimal('0')) else round((order.grand_total - order.shipping_cost) * (gst_rate / (Decimal('100') + gst_rate)), 2)
    
    effective_items_total = order.subtotal - order.coupon_discount + order.shipping_cost
    taxable_value = max(Decimal('0.00'), effective_items_total - total_tax)

    is_intra_state = (buyer_state_code == SELLER_STATE_CODE or 'BIHAR' in buyer_state_upper)
    if is_intra_state:
        cgst_rate = gst_rate / Decimal('2')
        sgst_rate = gst_rate / Decimal('2')
        cgst_amount = round(total_tax / Decimal('2'), 2)
        sgst_amount = round(total_tax - cgst_amount, 2)
        igst_rate = Decimal('0')
        igst_amount = Decimal('0.00')
    else:
        cgst_rate = Decimal('0')
        sgst_rate = Decimal('0')
        cgst_amount = Decimal('0.00')
        sgst_amount = Decimal('0.00')
        igst_rate = gst_rate
        igst_amount = total_tax

    items = order.items.select_related('product').all()

    return {
        'order': order,
        'items': items,
        'invoice_number': f"INV-{order.id:06d}",
        'invoice_date': order.updated_at if order.updated_at else order.created_at,
        'place_of_supply': place_of_supply,
        'taxable_value': taxable_value,
        'total_tax': total_tax,
        'gst_rate': gst_rate,
        'is_intra_state': is_intra_state,
        'cgst_rate': cgst_rate,
        'sgst_rate': sgst_rate,
        'cgst_amount': cgst_amount,
        'sgst_amount': sgst_amount,
        'igst_rate': igst_rate,
        'igst_amount': igst_amount,
    }


class SecureOrderInvoiceView(View):
    """
    Token-based secure invoice view for guest checkout and order success page.
    Validates token matching order's invoice_access_token without enforcing login or 'delivered' status.
    """
    def get(self, request, order_number, token):
        try:
            order = Order.objects.get(order_number=order_number)
        except Order.DoesNotExist:
            raise Http404("Order not found.")

        if not order.is_invoice_token_valid(token):
            return HttpResponseForbidden("Invalid or unauthorized invoice access token.")

        context = build_invoice_context(order)
        return render(request, 'invoice.html', context)


class OrderInvoiceView(LoginRequiredMixin, View):
    """
    Tax Invoice View to generate and print GST-compliant tax invoice for delivered orders via account dashboard.
    """
    login_url = 'login'

    def get(self, request, order_id):
        target_str = str(order_id).strip()
        try:
            if target_str.isdigit():
                order = Order.objects.get(id=int(target_str))
            else:
                order = Order.objects.get(order_number=target_str)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
            return redirect('account_orders')

        # Access permission: Order must belong to logged in user (or user is staff)
        if order.user != request.user and not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Access denied to this order invoice.")
            return redirect('account_orders')

        # Security check: Tax invoice is only accessible if order status is 'delivered'
        if order.order_status != 'delivered' and not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Tax Invoice is only available for delivered orders.")
            return redirect('account_orders')

        context = build_invoice_context(order)
        return render(request, 'invoice.html', context)



class WishlistView(TemplateView):
    """
    Wishlist View for authenticated users and guest sessions.
    """
    template_name = 'wishlist.html'

    def get(self, request, *args, **kwargs):
        session_key = _cart_id(request)
        if request.user.is_authenticated:
            wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product', 'product__category')
        else:
            wishlist_items = Wishlist.objects.filter(session_key=session_key, user__isnull=True).select_related('product', 'product__category')

        context = {
            'wishlist_items': wishlist_items,
            'wishlist_count': wishlist_items.count(),
        }
        return render_account_page(request, self.template_name, context)


class RemoveFromWishlistView(View):
    """
    Remove product item from wishlist.
    """
    def get(self, request, product_id):
        session_key = _cart_id(request)
        if request.user.is_authenticated:
            deleted_count, _ = Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
        else:
            deleted_count, _ = Wishlist.objects.filter(session_key=session_key, user__isnull=True, product_id=product_id).delete()

        if deleted_count > 0:
            messages.success(request, "Product removed from your wishlist.")
        return redirect('wishlist')


class ToggleWishlistView(View):
    """
    Toggle product item in wishlist via AJAX/HTMX or GET/POST.
    """
    def dispatch(self, request, product_id, *args, **kwargs):
        session_key = _cart_id(request)
        if request.user.is_authenticated:
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product_id=product_id
            )
        else:
            wishlist_item, created = Wishlist.objects.get_or_create(
                session_key=session_key,
                user__isnull=True,
                product_id=product_id
            )

        if not created:
            wishlist_item.delete()
            in_wishlist = False
            msg = "Product removed from your wishlist."
        else:
            in_wishlist = True
            msg = "Product added to your wishlist!"

        if request.user.is_authenticated:
            user_count = Wishlist.objects.filter(user=request.user).count()
        else:
            user_count = Wishlist.objects.filter(session_key=session_key, user__isnull=True).count()

        request.session['wishlist_count'] = user_count

        if request.method == 'POST' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'in_wishlist': in_wishlist,
                'wishlist_count': user_count,
                'message': msg
            })

        messages.success(request, msg)
        return redirect(safe_referer(request, 'wishlist'))


class ProfileView(LoginRequiredMixin, View):
    """
    User Profile View handling GET and POST profile updates with validation and HTMX partial support.
    """
    login_url = 'login'

    def get(self, request):
        context = {
            'user': request.user,
            'success_msg': None,
            'error_msg': None,
        }
        return render_account_page(request, 'profile.html', context)

    def post(self, request):
        user = request.user
        error_msg = None
        success_msg = None

        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()

        if not email:
            error_msg = "Email address is required."
        elif CustomUser.objects.filter(email=email).exclude(pk=user.pk).exists():
            error_msg = "This email address is already registered with another account."
        elif phone_number and CustomUser.objects.filter(phone_number=phone_number).exclude(pk=user.pk).exists():
            error_msg = "This phone number is already registered with another account."
        else:
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_number = phone_number if phone_number else None

            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']

            user.save()
            success_msg = "Profile details updated successfully!"

        context = {
            'user': user,
            'success_msg': success_msg,
            'error_msg': error_msg,
        }

        if request.headers.get('HX-Request') and request.headers.get('HX-Target') not in ['account-main-content', '#account-main-content']:
            return render(request, 'partials/profile_form_card.html', context)

        return render_account_page(request, 'profile.html', context)


class AddressesView(LoginRequiredMixin, TemplateView):
    """
    Saved Addresses View for managing delivery addresses.
    """
    login_url = 'login'
    template_name = 'addresses.html'

    def get(self, request, *args, **kwargs):
        addresses = UserAddress.objects.filter(user=request.user).order_by('id')
        context = {'addresses': addresses}
        return render_account_page(request, self.template_name, context)
