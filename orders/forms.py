from django import forms
from users.models import ShippingAddress, PaymentMethod
from promotions.models import Promotion
from .models import OrderItem

class ShippingAddressSelectForm(forms.Form):
    shipping_address = forms.ModelChoiceField(
        queryset=ShippingAddress.objects.none(), 
        widget=forms.RadioSelect,
        empty_label=None,
        label="Select a Shipping Address"
    )

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['shipping_address'].queryset = ShippingAddress.objects.filter(user=user)
            default_address = ShippingAddress.objects.filter(user=user, is_default=True).first()
            if default_address:
                self.fields['shipping_address'].initial = default_address

class PaymentMethodSelectForm(forms.Form):
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
        widget=forms.TextInput(attrs={'placeholder': 'Enter promo code', 'class': 'form-control'})
    )

    def clean_promo_code(self):
        promo_code = self.cleaned_data.get('promo_code')
        if not promo_code:
            return None

        try:
            promo = Promotion.objects.get(promo_code__iexact=promo_code)
            if not promo.is_valid():
                raise forms.ValidationError("This promotion is expired or invalid.")
        except Promotion.DoesNotExist:
            raise forms.ValidationError("Invalid promotion code.")
        
        return promo

# --- NEW RETURN REQUEST FORM ---

class ReturnRequestForm(forms.Form):
    """
    A form for users to select items from an order to return and provide a reason.
    """
    # This field allows selecting multiple items from an order.
    # It will be displayed as a series of checkboxes.
    items_to_return = forms.ModelMultipleChoiceField(
        queryset=OrderItem.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Select the item(s) you wish to return",
        required=True
    )
    
    # A text area for the user to explain why they are returning the items.
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        label="Reason for return",
        required=True
    )

    def __init__(self, *args, order=None, **kwargs):
        """
        The __init__ method is overridden to dynamically populate the 'items_to_return'
        queryset with only the items from the specific order being processed.
        """
        super().__init__(*args, **kwargs)
        if order:
            # Set the queryset for the items field to the items of the passed-in order.
            self.fields['items_to_return'].queryset = order.items.all()
