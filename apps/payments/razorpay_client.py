import hmac
import hashlib
from decimal import Decimal
from django.conf import settings
import razorpay
from razorpay.errors import SignatureVerificationError


class RazorpayClientHelper:
    """
    Utility wrapper for Razorpay payment gateway operations.
    Loads keys dynamically from settings / environment.
    """
    def __init__(self):
        self.key_id = getattr(settings, 'RAZORPAY_KEY_ID', '')
        self.key_secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
        self.webhook_secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')

        if self.key_id and self.key_secret:
            self.client = razorpay.Client(auth=(self.key_id, self.key_secret))
        else:
            self.client = None

    def is_configured(self):
        return self.client is not None or getattr(settings, 'DEBUG', False)

    def create_razorpay_order(self, order_number, amount):
        """
        Creates a Razorpay order for the specified amount (in INR Decimal).
        Returns the created Razorpay order payload.
        """
        if not self.client:
            if getattr(settings, 'DEBUG', False):
                # Return dummy order payload for local test mode without real API keys
                import time
                dummy_id = f"order_mock_{int(time.time())}"
                return {
                    'id': dummy_id,
                    'entity': 'order',
                    'amount': int(Decimal(str(amount)) * 100),
                    'currency': 'INR',
                    'receipt': order_number,
                    'status': 'created'
                }
            raise ValueError("Razorpay credentials (RAZORPAY_KEY_ID & RAZORPAY_KEY_SECRET) are not configured.")

        amount_in_paise = int(Decimal(str(amount)) * 100)
        razorpay_order = self.client.order.create({
            'amount': amount_in_paise,
            'currency': 'INR',
            'payment_capture': '1',
            'notes': {
                'order_number': str(order_number)
            }
        })
        return razorpay_order

    def verify_payment_signature(self, razorpay_order_id, razorpay_payment_id, razorpay_signature):
        """
        Verifies payment signature received from client after successful Razorpay checkout.
        """
        if not self.client:
            return getattr(settings, 'DEBUG', False)

        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            return True
        except SignatureVerificationError:
            return False
        except Exception:
            return False

    def verify_webhook_signature(self, body_bytes, signature_header):
        """
        Verifies server-to-server webhook signature provided in X-Razorpay-Signature header.
        """
        if not self.webhook_secret:
            if getattr(settings, 'DEBUG', False):
                return True
            return False

        if not signature_header:
            return False

        try:
            expected_signature = hmac.new(
                key=self.webhook_secret.encode('utf-8'),
                msg=body_bytes,
                digestmod=hashlib.sha256
            ).hexdigest()
            return hmac.compare_digest(expected_signature, signature_header)
        except Exception:
            return False
