from django import forms
from users.models import ShippingAddress, PaymentMethod
from promotions.models import Promotion

class ShippingAddressSelectForm(forms.Form):
    # This field will be populated with the user's saved addresses.
    # The 'widget=forms.RadioSelect' makes them appear as radio buttons.
    shipping_address = forms.ModelChoiceField(
        queryset=ShippingAddress.objects.none(), 
        widget=forms.RadioSelect,
        empty_label=None,
        label="Select a Shipping Address"
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            # We dynamically set the queryset to only show addresses for the current user.
            self.fields['shipping_address'].queryset = ShippingAddress.objects.filter(user=user)
            # Set the default choice to the user's default address.
            default_address = ShippingAddress.objects.filter(user=user, is_default=True).first()
            if default_address:
                self.fields['shipping_address'].initial = default_address

class PaymentMethodSelectForm(forms.Form):
    # This field will be populated with the user's saved payment methods.
    payment_method = forms.ModelChoiceField(
        queryset=PaymentMethod.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None,
        label="Select a Payment Method"
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['payment_method'].queryset = PaymentMethod.objects.filter(user=user)
            default_payment = PaymentMethod.objects.filter(user=user, is_default=True).first()
            if default_payment:
                self.fields['payment_method'].initial = default_payment


class PromotionApplyForm(forms.Form):
    promo_code = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter promo code'})
    )

    def clean_promo_code(self):
        promo_code = self.cleaned_data.get('promo_code')
        if not promo_code:
            return None # No code entered, which is fine.

        try:
            promo = Promotion.objects.get(promo_code__iexact=promo_code)
            if not promo.is_valid():
                raise forms.ValidationError("This promotion is expired or invalid.")
        except Promotion.DoesNotExist:
            raise forms.ValidationError("Invalid promotion code.")
        
        return promo # Return the valid Promotion object.
