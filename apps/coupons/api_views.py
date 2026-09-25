from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from apps.cart.services import apply_coupon_to_subtotal
from apps.coupons.serializers import CouponApplySerializer


class ApplyCouponAPIView(APIView):
    """
    POST /api/v1/coupons/apply/
    Validates and calculates coupon discount for a given subtotal.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(request=CouponApplySerializer)
    def post(self, request, *args, **kwargs):
        serializer = CouponApplySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        subtotal = serializer.validated_data['cart_subtotal']

        is_valid, discount_amount, message, coupon = apply_coupon_to_subtotal(code, subtotal)

        if not is_valid:
            if 'coupon_code' in request.session:
                del request.session['coupon_code']
                request.session.modified = True
            return Response({
                'success': False,
                'message': message,
                'discount_amount': '0.00'
            }, status=status.HTTP_400_BAD_REQUEST)

        request.session['coupon_code'] = coupon.code
        request.session.modified = True

        return Response({
            'success': True,
            'message': message,
            'code': coupon.code,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value,
            'discount_amount': discount_amount
        }, status=status.HTTP_200_OK)


class RemoveCouponAPIView(APIView):
    """
    POST /api/v1/coupons/remove/
    Removes active coupon from request session.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        if 'coupon_code' in request.session:
            del request.session['coupon_code']
            request.session.modified = True

        return Response({
            'success': True,
            'message': 'Coupon removed successfully.'
        }, status=status.HTTP_200_OK)
