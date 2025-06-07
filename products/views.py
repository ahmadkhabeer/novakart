from django.shortcuts import render, get_object_or_404
from .models import Product
from carts.forms import ChartAddProductForm

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    cart_product_form = ChartAddProductForm()
    context = {
        'product': product,
        'cart_product_form': cart_product_form
    }
    
    return render(request, 'products/product_detail.html', context)
