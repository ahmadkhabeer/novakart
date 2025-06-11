from django import forms
from .models import Seller

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
