from django.shortcuts import render, get_object_or_404
from products.models import Category, Product

# def home(request):
#     return render(request, 'shop/home.html', {"welcome_message":"Welcome to NovaKart 🛒"})

def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category, slug= category_slug)
        products = products.filter(category= category)
    
    context = {
        'category': category,
        'categories': categories,
        'products': products
        
    }
    
    return render(request, 'shop/product_list.html', context)
