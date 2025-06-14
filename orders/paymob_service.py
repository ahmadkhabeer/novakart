import requests
import hmac
import hashlib
from django.conf import settings

class PaymobService:
    BASE_URL = "https://accept.paymob.com/api"
    API_KEY = settings.PAYMOB_API_KEY
    HMAC_SECRET = settings.PAYMOB_HMAC_SECRET

    def get_auth_token(self):
        """ Step 1: Authentication Request """
        url = f"{self.BASE_URL}/auth/tokens"
        payload = {"api_key": self.API_KEY}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json().get('token')

    def create_order(self, auth_token, order):
        """ Step 2: Order Registration Request """
        url = f"{self.BASE_URL}/ecommerce/orders"
        headers = {"Authorization": f"Bearer {auth_token}"}
        # Paymob requires amount in piasters (cents)
        amount_cents = int(order.total_paid * 100)
        
        payload = {
            "auth_token": auth_token,
            "delivery_needed": "false",
            "amount_cents": str(amount_cents),
            "currency": "EGP",
            "merchant_order_id": str(order.id),
            "items": [] # You can add item details here if you want
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_payment_key(self, auth_token, order_data, order):
        """ Step 3: Payment Key Request """
        url = f"{self.BASE_URL}/acceptance/payment_keys"
        headers = {"Authorization": f"Bearer {auth_token}"}
        amount_cents = int(order.total_paid * 100)
        
        # User details can be passed here
        billing_data = {
            "apartment": "NA",
            "email": order.user.email,
            "floor": "NA",
            "first_name": order.user.first_name or order.user.username,
            "street": "NA",
            "building": "NA",
            "phone_number": "+201111111111", # Placeholder
            "shipping_method": "NA",
            "postal_code": "NA",
            "city": "NA",
            "country": "EG",
            "last_name": order.user.last_name or "NA",
            "state": "NA"
        }
        
        payload = {
            "auth_token": auth_token,
            "amount_cents": str(amount_cents),
            "expiration": 3600,
            "order_id": order_data.get('id'),
            "billing_data": billing_data,
            "currency": "EGP",
            "integration_id": settings.PAYMOB_INTEGRATION_ID,
            "lock_order_when_paid": "true"
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json().get('token')

    def get_payment_iframe_url(self, payment_key):
        return f"https://accept.paymob.com/api/acceptance/iframes/{settings.PAYMOB_IFRAME_ID}?payment_token={payment_key}"

    def validate_hmac(self, callback_data):
        """ Validates the HMAC to ensure the callback is from Paymob """
        hmac_keys = [
            'amount_cents', 'created_at', 'currency', 'error_occured', 'has_parent_transaction',
            'id', 'integration_id', 'is_3d_secure', 'is_auth', 'is_capture', 'is_refunded',
            'is_standalone_payment', 'is_voided', 'order', 'owner', 'pending', 'source_data_pan',
            'source_data_sub_type', 'source_data_type', 'success'
        ]
        
        concatenated_string = ""
        for key in sorted(hmac_keys):
            value = callback_data.get(key)
            if isinstance(value, bool):
                concatenated_string += str(value).lower()
            else:
                concatenated_string += str(value)

        h = hmac.new(self.HMAC_SECRET.encode('utf-8'), concatenated_string.encode('utf-8'), hashlib.sha512)
        calculated_hmac = h.hexdigest()
        
        return hmac.compare_digest(calculated_hmac, callback_data.get('hmac'))
