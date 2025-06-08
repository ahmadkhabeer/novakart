from django.shortcuts import render, get_object_or_404
from .models import Product
from marketplace.models import Offer

def product_detail(request, parent_asin):
    """
    Displays the details for a parent product, including its variants and the best offers for each.
    """
    parent_product = get_object_or_404(Product, parent_asin=parent_asin, is_variation_parent=True)
    variants = parent_product.variants.all()
    
    # For a true Amazon-like experience, you'd have a complex algorithm to select the "Buy Box" winner.
    # For now, we'll find the best (lowest priced) active offer for each variant.
    
    variants_with_offers = []
    for variant in variants:
        best_offer = Offer.objects.filter(variant=variant, is_active=True).order_by('price').first()
        variants_with_offers.append({
            'variant': variant,
            'best_offer': best_offer
        })

    # The "main offer" for the page could be the best offer from the first variant, or another logic.
    main_offer = variants_with_offers[0]['best_offer'] if variants_with_offers else None

    context = {
        'product': parent_product,
        'variants_with_offers': variants_with_offers,
        'main_offer': main_offer,
    }
    return render(request, 'products/product_detail.html', context)
