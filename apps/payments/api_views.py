import json
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from drf_spectacular.utils import extend_schema

from apps.cart.models import Order
from apps.payments.serializers import RazorpayCreateOrderSerializer, RazorpayVerifyPaymentSerializer
from apps.payments.razorpay_client import RazorpayClientHelper


class RazorpayCreateOrderAPIView(APIView):
    """
    POST /api/v1/payments/razorpay/create-order/
    Creates a Razorpay order for an existing pending Order instance.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RazorpayCreateOrderSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RazorpayCreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order_number = serializer.validated_data['order_number']

        order = get_object_or_404(Order, order_number=order_number)

        # Check access permission: logged in owner OR matching guest session/key
        guest_key = request.headers.get('X-Guest-Cart-Key', '')
        if order.user and (not request.user.is_authenticated or order.user != request.user):
            return Response({
                'success': False,
                'message': 'You do not have permission to initiate payment for this order.'
            }, status=status.HTTP_403_FORBIDDEN)

        helper = RazorpayClientHelper()
        try:
            rzp_order = helper.create_razorpay_order(order.order_number, order.grand_total)
            order.razorpay_order_id = rzp_order['id']
            order.payment_method = 'razorpay'
            order.save(update_fields=['razorpay_order_id', 'payment_method', 'updated_at'])

            return Response({
                'success': True,
                'key_id': helper.key_id,
                'amount': rzp_order['amount'],
                'currency': rzp_order.get('currency', 'INR'),
                'razorpay_order_id': rzp_order['id'],
                'order_number': order.order_number,
                'customer_name': order.full_name,
                'customer_email': order.email or '',
                'customer_phone': order.phone,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'success': False,
                'message': f"Failed to create Razorpay order: {str(e)}"
            }, status=status.HTTP_400_BAD_REQUEST)


class RazorpayVerifyPaymentAPIView(APIView):
    """
    POST /api/v1/payments/razorpay/verify/
    Verifies client-side Razorpay signature and updates Order payment status to 'paid'.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=RazorpayVerifyPaymentSerializer)
    def post(self, request, *args, **kwargs):
        serializer = RazorpayVerifyPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        order_number = serializer.validated_data['order_number']
        rzp_order_id = serializer.validated_data['razorpay_order_id']
        rzp_payment_id = serializer.validated_data['razorpay_payment_id']
        rzp_signature = serializer.validated_data['razorpay_signature']

        order = get_object_or_404(Order, order_number=order_number)

        # Idempotency check
        if order.payment_status == 'paid':
            return Response({
                'success': True,
                'message': 'Payment already verified and completed.',
                'order_number': order.order_number
            }, status=status.HTTP_200_OK)

        # Ensure razorpay_order_id matches the one generated for this order
        if order.razorpay_order_id and order.razorpay_order_id != rzp_order_id:
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status', 'updated_at'])
            return Response({
                'success': False,
                'message': 'Razorpay order ID mismatch.'
            }, status=status.HTTP_400_BAD_REQUEST)

        helper = RazorpayClientHelper()
        verified = helper.verify_payment_signature(rzp_order_id, rzp_payment_id, rzp_signature)

        if verified:
            order.payment_status = 'paid'
            order.order_status = 'processing'
            order.razorpay_order_id = rzp_order_id
            order.razorpay_payment_id = rzp_payment_id
            order.razorpay_signature = rzp_signature
            order.save(update_fields=[
                'payment_status', 'order_status', 'razorpay_order_id',
                'razorpay_payment_id', 'razorpay_signature', 'updated_at'
            ])

            return Response({
                'success': True,
                'message': 'Payment verified successfully.',
                'order_number': order.order_number,
                'invoice_token': str(order.invoice_access_token)
            }, status=status.HTTP_200_OK)
        else:
            order.payment_status = 'failed'
            order.save(update_fields=['payment_status', 'updated_at'])
            return Response({
                'success': False,
                'message': 'Razorpay signature verification failed.'
            }, status=status.HTTP_400_BAD_REQUEST)


class RazorpayWebhookAPIView(APIView):
    """
    POST /api/v1/payments/razorpay/webhook/
    Server-to-server webhook callback directly called by Razorpay.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        signature = request.headers.get('X-Razorpay-Signature', '')
        raw_body = request.body

        helper = RazorpayClientHelper()
        if not helper.verify_webhook_signature(raw_body, signature):
            return Response({
                'success': False,
                'message': 'Invalid webhook signature.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except Exception:
            return Response({'success': False, 'message': 'Invalid JSON payload.'}, status=status.HTTP_400_BAD_REQUEST)

        event = payload.get('event', '')

        if event in ['payment.captured', 'order.paid']:
            payment_entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
            rzp_order_id = payment_entity.get('order_id')
            rzp_payment_id = payment_entity.get('id')
            notes = payment_entity.get('notes', {})
            order_number = notes.get('order_number')

            order = None
            if rzp_order_id:
                order = Order.objects.filter(razorpay_order_id=rzp_order_id).first()
            if not order and order_number:
                order = Order.objects.filter(order_number=order_number).first()

            if order and order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.order_status = 'processing'
                if rzp_payment_id:
                    order.razorpay_payment_id = rzp_payment_id
                order.save(update_fields=['payment_status', 'order_status', 'razorpay_payment_id', 'updated_at'])

        return Response({'success': True, 'message': 'Webhook received.'}, status=status.HTTP_200_OK)
