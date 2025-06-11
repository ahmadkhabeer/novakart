from django.shortcuts import render, get_object_or_404
from .models import Product
from reviews.models import ProductReview
from orders.models import OrderItem

def product_detail(request, parent_asin):
    """
    Displays the details for a parent product, its variants, offers, images, and reviews.
    """
    product = get_object_or_404(Product, parent_asin=parent_asin, is_variation_parent=True)
    
    # Fetch all related data efficiently
    variants = product.variants.prefetch_related(
        'offers__seller',
        'attributes__attribute_value__attribute'
    ).all()
    images = product.images.all()
    reviews = product.reviews.select_related('customer').order_by('-created_at')

    # Check if the current user is eligible to write a review
    can_review = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            offer__variant__parent_product=product
        ).exists()
        already_reviewed = reviews.filter(customer=request.user).exists()
        if has_purchased and not already_reviewed:
            can_review = True
    
    # Find the best offer to display in the "buy box"
    main_offer = None
    if variants and variants.first().offers.exists():
        main_offer = variants.first().offers.order_by('price').first()

    context = {
        'product': product,
        'variants': variants,
        'main_offer': main_offer,
        'images': images,
        'reviews': reviews,
        'can_review': can_review,
    }
    return render(request, 'products/product_detail.html', context)
