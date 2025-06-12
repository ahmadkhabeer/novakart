from django import forms
from .models import ProductReview

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        # We only want the user to input these fields
        fields = ['rating', 'title', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A short summary of your review'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Tell us more about your experience...'}),
        }
        labels = {
            'rating': "Your overall rating",
            'title': "Review headline",
            'text': "Your written review"
        }
