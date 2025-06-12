from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from collections import OrderedDict
import json

from .models import Product, ProductVariant
from reviews.models import ProductReview
from orders.models import OrderItem

def product_detail(request, parent_asin):
    product = get_object_or_404(Product, parent_asin=parent_asin)
    variants = product.variants.prefetch_related(
        'offers__seller', 'attributes__attribute', 'images'
    ).order_by('id')

    # --- Fetch reviews for display ---
    reviews = product.reviews.select_related('customer').order_by('-created_at')

    # --- Check if user is eligible to write a review ---
    can_review = False
    if request.user.is_authenticated:
        # Check if user has a paid order for any variant of this product
        has_purchased = OrderItem.objects.filter(
            order__user=request.user,
            offer__variant__in=variants,
            order__paid=True
        ).exists()
        # Check if they haven't already reviewed it
        already_reviewed = reviews.filter(customer=request.user).exists()
        if has_purchased and not already_reviewed:
            can_review = True
            
    # --- Logic to group attributes for the template ---
    attributes_data = OrderedDict()
    for variant in variants:
        for attr_value in variant.attributes.all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes_data:
                attributes_data[attr_name] = set()
            attributes_data[attr_name].add(attr_value)
    for attr_name in attributes_data:
        attributes_data[attr_name] = sorted(list(attributes_data[attr_name]), key=lambda x: x.value)

    # --- Logic to create a JSON map for JavaScript ---
    variant_map = {}
    for variant in variants:
        key = "-".join(str(a.id) for a in variant.attributes.all().order_by('id'))
        best_offer = variant.get_best_offer()
        variant_map[key] = {
            'id': variant.id,
            'price': f"{best_offer.price:.2f}" if best_offer else None,
            'in_stock': best_offer.quantity > 0 if best_offer else False,
            'image_urls': [img.image.url for img in variant.images.all()],
        }

    context = {
        'product': product,
        'main_offer': variants.first().get_best_offer() if variants and variants.first().offers.exists() else None,
        'parent_images': product.images.all(),
        'attributes_data': attributes_data,
        'variant_map_json': json.dumps(variant_map),
        'reviews': reviews,       # Pass reviews to template
        'can_review': can_review, # Pass eligibility flag
    }
    return render(request, 'products/product_detail.html', context)


def get_variant_data_api(request, variant_id):
    # ... (this view remains correct and unchanged)
    try:
        variant = ProductVariant.objects.prefetch_related('offers__seller', 'images').get(id=variant_id)
        best_offer = variant.get_best_offer()
        image_urls = [img.image.url for img in variant.images.all()]
        if not image_urls:
            image_urls = [img.image.url for img in variant.parent_product.images.all()]

        if best_offer:
            data = {
                'offer_id': best_offer.id,
                'price': f"{best_offer.price:.2f}",
                'in_stock': best_offer.quantity > 0,
                'seller_name': best_offer.seller.name,
                'image_urls': image_urls,
            }
            return JsonResponse(data)
        else:
            return JsonResponse({'in_stock': False, 'image_urls': image_urls}, status=404)
    except ProductVariant.DoesNotExist:
        return JsonResponse({'error': 'Variant not found'}, status=404)
