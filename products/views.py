import json
from django.shortcuts import render, get_object_or_404
from collections import OrderedDict

from .models import Product, ProductVariant
from reviews.models import ProductReview, ProductQuestion
from orders.models import OrderItem
from reviews.forms import QuestionForm

def product_detail(request, parent_asin):
    """
    Displays the details for a parent product. This version pre-loads all variant
    data into the template for faster, more reliable JavaScript interaction.
    """
    product = get_object_or_404(Product, parent_asin=parent_asin)
    
    variants = product.variants.prefetch_related(
        'offers__seller', 
        'attributes__attribute', 
        'images'
    ).order_by('id')
    
    # --- Logic to group attributes for easy display in the template ---
    attributes_data = OrderedDict()
    if variants:
        # A more efficient way to get all unique attribute values for this product
        all_attribute_values = ProductVariant.objects.filter(parent_product=product).values_list(
            'attributes__id', 
            'attributes__value',
            'attributes__attribute__name', 
        ).distinct().order_by('attributes__attribute__name', 'attributes__value')

        for attr_id, attr_value, attr_name in all_attribute_values:
            if attr_name not in attributes_data:
                attributes_data[attr_name] = []
            
            value_dict = {'id': attr_id, 'value': attr_value}
            if value_dict not in attributes_data[attr_name]:
                attributes_data[attr_name].append(value_dict)

    # --- Create a comprehensive JSON data map for JavaScript ---
    # This map links an attribute combination key to ALL its necessary data.
    variant_data = {}
    for variant in variants:
        # Sort attribute value IDs to create a consistent, order-independent key
        key = "-".join(str(a.id) for a in variant.attributes.all().order_by('id'))
        best_offer = variant.get_best_offer()
        
        variant_images = [img.image.url for img in variant.images.all()]
        if not variant_images: # Fallback to parent images if variant has none
            variant_images = [img.image.url for img in product.images.all()]

        variant_data[key] = {
            'price': f"{best_offer.price:.2f}" if best_offer else None,
            'in_stock': best_offer.quantity > 0 if best_offer else False,
            'offer_id': best_offer.id if best_offer else None,
            'image_urls': variant_images
        }
    
    # --- Prepare all context for the template ---
    context = {
        'product': product,
        'main_offer': variants.first().get_best_offer() if variants and variants.first().offers.exists() else None,
        'parent_images': product.images.all(),
        'attributes_data': attributes_data,
        'variant_data_json': json.dumps(variant_data),
        'reviews': product.reviews.select_related('customer').order_by('-created_at'),
        'questions': product.questions.select_related('customer').prefetch_related('answers__customer').order_by('-created_at'),
        'question_form': QuestionForm(),
        'can_review': False, # Default value
    }

    # Check for review eligibility only if a user is logged in
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user, 
            offer__variant__in=variants,
            order__paid=True
        ).exists()
        already_reviewed = context['reviews'].filter(customer=request.user).exists()
        if has_purchased and not already_reviewed:
            context['can_review'] = True

    return render(request, 'products/product_detail.html', context)
