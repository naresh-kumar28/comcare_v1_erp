from decimal import Decimal
from rest_framework import status, generics, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.cart.models import Cart, CartItem, UserAddress, ShippingConfig, Order, OrderItem
from apps.store.models import Product
from apps.cart.serializers import (
    CartSerializer,
    CartItemSerializer,
    UserAddressSerializer,
    ShippingConfigSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderCreateSerializer,
)
from apps.cart.services import (
    get_guest_session_key,
    get_or_create_cart,
    merge_guest_cart,
    calculate_cart_totals,
    build_order_from_cart,
)
from apps.accounts.views import build_invoice_context
from common.permissions import IsOwnerOrAdmin


# ============================================================================
# Cart API Views
# ============================================================================

class CartAPIView(APIView):
    """
    GET /api/v1/cart/
    Retrieves active cart for authenticated user or guest (via X-Guest-Cart-Key header).
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        session_key = get_guest_session_key(request)
        cart = get_or_create_cart(user=request.user, session_key=session_key, create=False)
        totals = calculate_cart_totals(cart=cart, coupon_code=request.session.get('coupon_code'))

        return Response({
            'success': True,
            'cart': totals
        }, status=status.HTTP_200_OK)


class CartItemAddAPIView(APIView):
    """
    POST /api/v1/cart/items/
    Adds an item to the current user's or guest's active cart.
    Payload: { "product_id": 1, "quantity": 2 }
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        try:
            quantity = int(request.data.get('quantity', 1))
            if quantity < 1:
                quantity = 1
        except (ValueError, TypeError):
            quantity = 1

        if not product_id:
            return Response({'success': False, 'message': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id, is_active=True)
        session_key = get_guest_session_key(request)
        cart = get_or_create_cart(user=request.user, session_key=session_key, create=True)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                'quantity': quantity,
                'unit_price': product.selling_price,
                'is_active': True,
            }
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        totals = calculate_cart_totals(cart=cart, coupon_code=request.session.get('coupon_code'))
        return Response({
            'success': True,
            'message': f"Added {product.title} to cart.",
            'cart': totals
        }, status=status.HTTP_201_CREATED)


class CartItemUpdateDeleteAPIView(APIView):
    """
    PATCH /api/v1/cart/items/{id}/   → Update quantity
    DELETE /api/v1/cart/items/{id}/  → Remove item from cart
    """
    permission_classes = [permissions.AllowAny]

    def patch(self, request, pk, *args, **kwargs):
        session_key = get_guest_session_key(request)
        cart = get_or_create_cart(user=request.user, session_key=session_key, create=False)
        if not cart:
            return Response({'success': False, 'message': 'Cart not found.'}, status=status.HTTP_404_NOT_FOUND)

        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)

        try:
            quantity = int(request.data.get('quantity', 1))
        except (ValueError, TypeError):
            quantity = 1

        if quantity <= 0:
            cart_item.delete()
            msg = "Item removed from cart."
        else:
            cart_item.quantity = quantity
            cart_item.save()
            msg = "Cart item quantity updated."

        totals = calculate_cart_totals(cart=cart, coupon_code=request.session.get('coupon_code'))
        return Response({
            'success': True,
            'message': msg,
            'cart': totals
        }, status=status.HTTP_200_OK)

    def delete(self, request, pk, *args, **kwargs):
        session_key = get_guest_session_key(request)
        cart = get_or_create_cart(user=request.user, session_key=session_key, create=False)
        if cart:
            CartItem.objects.filter(id=pk, cart=cart).delete()

        totals = calculate_cart_totals(cart=cart, coupon_code=request.session.get('coupon_code'))
        return Response({
            'success': True,
            'message': 'Item removed from cart.',
            'cart': totals
        }, status=status.HTTP_200_OK)


class CartMergeAPIView(APIView):
    """
    POST /api/v1/cart/merge/
    Merges guest cart items into the authenticated user's cart.
    Requires authentication.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_key = get_guest_session_key(request)
        merged_cart = merge_guest_cart(request.user, session_key)
        totals = calculate_cart_totals(cart=merged_cart, coupon_code=request.session.get('coupon_code'))

        return Response({
            'success': True,
            'message': 'Guest cart merged successfully.',
            'cart': totals
        }, status=status.HTTP_200_OK)


# ============================================================================
# User Addresses API Views
# ============================================================================

class UserAddressListCreateAPIView(generics.ListCreateAPIView):
    """
    GET /api/v1/addresses/    → List saved addresses
    POST /api/v1/addresses/   → Create a new saved address
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserAddress.objects.filter(user=self.request.user).order_by('-is_default', '-id')
        session_key = get_guest_session_key(self.request)
        return UserAddress.objects.filter(session_key=session_key).order_by('-is_default', '-id')

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            session_key = get_guest_session_key(self.request)
            serializer.save(session_key=session_key)


class UserAddressDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    PATCH /api/v1/addresses/{id}/   → Update address
    DELETE /api/v1/addresses/{id}/  → Delete address
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserAddress.objects.filter(user=self.request.user)
        session_key = get_guest_session_key(self.request)
        return UserAddress.objects.filter(session_key=session_key)


class UserAddressSetDefaultAPIView(APIView):
    """
    POST /api/v1/addresses/{id}/set-default/
    Sets the specified address as default for the user or session.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            address = get_object_or_404(UserAddress, id=pk, user=request.user)
            UserAddress.objects.filter(user=request.user).update(is_default=False)
        else:
            session_key = get_guest_session_key(request)
            address = get_object_or_404(UserAddress, id=pk, session_key=session_key)
            UserAddress.objects.filter(session_key=session_key).update(is_default=False)

        address.is_default = True
        address.save()

        return Response({
            'success': True,
            'message': 'Default address updated.',
            'address': UserAddressSerializer(address).data
        }, status=status.HTTP_200_OK)


# ============================================================================
# Shipping Configuration API View
# ============================================================================

class ShippingConfigAPIView(APIView):
    """
    GET /api/v1/shipping-config/
    Public read-only endpoint returning current shipping rules.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        config = ShippingConfig.get_config()
        serializer = ShippingConfigSerializer(config)
        return Response({
            'success': True,
            'config': serializer.data
        }, status=status.HTTP_200_OK)


# ============================================================================
# Orders API Views
# ============================================================================

class OrderListCreateAPIView(APIView):
    """
    GET /api/v1/orders/   → List orders for current user or guest key
    POST /api/v1/orders/  → Place an order from active cart
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            orders_qs = Order.objects.filter(user=request.user).prefetch_related('items').order_by('-created_at')
        else:
            session_key = get_guest_session_key(request)
            orders_qs = Order.objects.filter(session_key=session_key).prefetch_related('items').order_by('-created_at')

        serializer = OrderListSerializer(orders_qs, many=True)
        return Response({
            'success': True,
            'results': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(request=OrderCreateSerializer)
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        address_id = serializer.validated_data.get('address_id')
        payment_method = serializer.validated_data.get('payment_method', 'cod')
        coupon_code = serializer.validated_data.get('coupon_code') or request.session.get('coupon_code')

        session_key = get_guest_session_key(request)
        user = request.user if request.user.is_authenticated else None

        cart = get_or_create_cart(user=user, session_key=session_key, create=False)
        if not cart or cart.items.filter(is_active=True).count() == 0:
            return Response({
                'success': False,
                'message': 'Cart is empty. Add products before checkout.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Address resolution
        address = None
        if address_id:
            if user:
                address = UserAddress.objects.filter(id=address_id, user=user).first()
            else:
                address = UserAddress.objects.filter(id=address_id, session_key=session_key).first()

        if not address:
            # Inline address
            full_name = serializer.validated_data.get('full_name')
            phone = serializer.validated_data.get('phone')
            address_line1 = serializer.validated_data.get('address_line1')
            pincode = serializer.validated_data.get('pincode')

            if full_name and phone and address_line1 and pincode:
                address = UserAddress.objects.create(
                    user=user,
                    session_key=session_key if not user else None,
                    full_name=full_name,
                    phone=phone,
                    email=serializer.validated_data.get('email', ''),
                    address_line1=address_line1,
                    address_line2=serializer.validated_data.get('address_line2', ''),
                    city=serializer.validated_data.get('city', 'Purnea'),
                    state=serializer.validated_data.get('state', 'Bihar'),
                    pincode=pincode,
                    is_default=True
                )
            else:
                return Response({
                    'success': False,
                    'message': 'Valid delivery address is required.'
                }, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = build_order_from_cart(
                cart=cart,
                address=address,
                payment_method=payment_method,
                coupon_code=coupon_code,
                user=user,
                session_key=session_key
            )
        except Exception as e:
            return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        order_data = OrderDetailSerializer(order).data

        # If Razorpay payment method requested
        if payment_method == 'razorpay':
            from apps.payments.razorpay_client import RazorpayClientHelper
            helper = RazorpayClientHelper()
            try:
                rzp_order = helper.create_razorpay_order(order.order_number, order.grand_total)
                order.razorpay_order_id = rzp_order['id']
                order.save(update_fields=['razorpay_order_id'])
                return Response({
                    'success': True,
                    'message': 'Order created. Proceed to payment.',
                    'order': order_data,
                    'razorpay': {
                        'key_id': helper.key_id,
                        'amount': rzp_order['amount'],
                        'currency': rzp_order.get('currency', 'INR'),
                        'razorpay_order_id': rzp_order['id'],
                    }
                }, status=status.HTTP_201_CREATED)
            except Exception as ex:
                pass

        return Response({
            'success': True,
            'message': 'Order placed successfully.',
            'order': order_data
        }, status=status.HTTP_201_CREATED)


class OrderDetailAPIView(APIView):
    """
    GET /api/v1/orders/{order_number}/
    Retrieves full details for a specific order.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, order_number, *args, **kwargs):
        order = get_object_or_404(Order, order_number=order_number)

        # Security check: owner, staff, or matching session/token
        session_key = get_guest_session_key(request)
        is_owner = (request.user.is_authenticated and order.user == request.user)
        is_staff = (request.user.is_authenticated and request.user.is_staff)
        is_guest_session = (order.session_key and order.session_key == session_key)
        token = request.GET.get('token')
        is_valid_token = order.is_invoice_token_valid(token) if token else False

        if not (is_owner or is_staff or is_guest_session or is_valid_token):
            return Response({
                'success': False,
                'message': 'You do not have permission to view this order.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderDetailSerializer(order)
        return Response({
            'success': True,
            'order': serializer.data
        }, status=status.HTTP_200_OK)


class OrderCancelAPIView(APIView):
    """
    POST /api/v1/orders/{id}/cancel/
    Cancels an order if its status is 'pending' or 'processing'.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated:
            order = get_object_or_404(Order, id=pk, user=request.user)
        else:
            session_key = get_guest_session_key(request)
            order = get_object_or_404(Order, id=pk, session_key=session_key)

        if order.order_status in ['pending', 'processing']:
            order.order_status = 'cancelled'
            order.save(update_fields=['order_status', 'updated_at'])
            return Response({
                'success': True,
                'message': f"Order #{order.order_number} cancelled successfully.",
                'order_number': order.order_number
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': f"Order cannot be cancelled in status '{order.get_order_status_display()}'."
            }, status=status.HTTP_400_BAD_REQUEST)


class OrderInvoiceAPIView(APIView):
    """
    GET /api/v1/orders/{order_number}/invoice/?token=<uuid>
    Returns GST-compliant tax invoice JSON data for rendering or printing.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, order_number, *args, **kwargs):
        order = get_object_or_404(Order, order_number=order_number)
        token = request.GET.get('token')

        is_owner = (request.user.is_authenticated and order.user == request.user)
        is_staff = (request.user.is_authenticated and request.user.is_staff)
        is_valid_token = order.is_invoice_token_valid(token) if token else False

        if not (is_owner or is_staff or is_valid_token):
            return Response({
                'success': False,
                'message': 'Invalid or unauthorized invoice access token.'
            }, status=status.HTTP_403_FORBIDDEN)

        context = build_invoice_context(order)

        items_data = []
        for item in context['items']:
            items_data.append({
                'product_title': item.product_title,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'total_price': item.total_price,
            })

        return Response({
            'success': True,
            'invoice_number': context['invoice_number'],
            'invoice_date': context['invoice_date'],
            'place_of_supply': context['place_of_supply'],
            'customer': {
                'full_name': order.full_name,
                'phone': order.phone,
                'email': order.email,
                'address_line1': order.address_line1,
                'address_line2': order.address_line2,
                'city': order.city,
                'state': order.state,
                'pincode': order.pincode,
            },
            'items': items_data,
            'taxable_value': context['taxable_value'],
            'total_tax': context['total_tax'],
            'gst_rate': context['gst_rate'],
            'is_intra_state': context['is_intra_state'],
            'cgst_amount': context['cgst_amount'],
            'sgst_amount': context['sgst_amount'],
            'igst_amount': context['igst_amount'],
            'subtotal': order.subtotal,
            'coupon_discount': order.coupon_discount,
            'shipping_cost': order.shipping_cost,
            'grand_total': order.grand_total,
        }, status=status.HTTP_200_OK)
