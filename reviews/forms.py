from django import forms
from .models import ProductReview, ProductQuestion, ProductAnswer

class ProductReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'title', 'text']
        widgets = {
            'rating': forms.Select(choices=[(i, f'{i} Stars') for i in range(1, 6)], attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'rating': "Your overall rating",
            'title': "Review headline",
            'text': "Your written review"
        }

# --- NEW Q&A FORMS ---
class QuestionForm(forms.ModelForm):
    class Meta:
        model = ProductQuestion
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ask a question about this product...'
            }),
        }
        labels = {
            'text': '' # Hide the label as the placeholder is sufficient
        }

class AnswerForm(forms.ModelForm):
    class Meta:
        model = ProductAnswer
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Provide an answer...'
            }),
        }
        labels = {
            'text': 'Your Answer'
        }
