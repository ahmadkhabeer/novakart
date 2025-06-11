from django import forms

class ProductFilterForm(forms.Form):
    SORT_CHOICES = (
        ('', 'Default'),
        ('price_asc', 'Price: Low to High'),
        ('price_desc', 'Price: High to Low'),
        ('name_asc', 'Name: A to Z'),
        ('name_desc', 'Name: Z to A'),
    )

    q = forms.CharField(label="Search", required=False, widget=forms.TextInput(attrs={'placeholder': 'Search products...', 'class': 'form-control'}))
    sort_by = forms.ChoiceField(label="Sort by", choices=SORT_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
