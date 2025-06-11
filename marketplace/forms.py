from django import forms
from .models import Seller, Offer

class SellerRegisterForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Business or Store Name'}),
        }
        labels = {
            'name': "Seller Name"
        }

# --- NEW OFFER FORM ---
class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        # We only want the seller to fill out these fields.
        # variant, seller, and is_active will be set programmatically in the view.
        fields = ['price', 'quantity', 'condition', 'fulfillment_type']
        widgets = {
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'fulfillment_type': forms.Select(attrs={'class': 'form-select'}),
        }
