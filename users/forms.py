from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, ShippingAddress

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [] # Add fields here like 'phone_number', 'profile_picture' when you add them to the model
        # For now, it's empty, but the structure is ready.

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        # Exclude 'user' because we will set it programmatically in the view.
        exclude = ('user',)

        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street Address, P.O. Box'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, unit, etc. (Optional)'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state_province_region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State / Province / Region'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postal Code'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Country'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number (Optional)'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
