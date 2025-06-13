import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from collections import OrderedDict

from .models import Product, ProductVariant, ProductRequest
from reviews.models import ProductReview, ProductQuestion
from orders.models import OrderItem
from reviews.forms import QuestionForm
from .forms import ProductRequestForm
from marketplace.decorators import seller_required

def product_detail(request, parent_asin):
    """
    Displays the details for a parent product, including variants, offers, 
    images, reviews, and the Q&A section.
    """
    product = get_object_or_404(Product, parent_asin=parent_asin)
    
    variants = product.variants.prefetch_related(
        'offers__seller', 
        'attributes__attribute', 
        'images'
    ).order_by('id')
    
    parent_images = product.images.all()
    reviews = product.reviews.select_related('customer').order_by('-created_at')
    questions = product.questions.select_related('customer').prefetch_related('answers__customer').order_by('-created_at')
    question_form = QuestionForm()
    
    can_review = False
    if request.user.is_authenticated:
        has_purchased = OrderItem.objects.filter(
            order__user=request.user, 
            offer__variant__in=variants,
            order__paid=True
        ).exists()
        already_reviewed = reviews.filter(customer=request.user).exists()
        if has_purchased and not already_reviewed:
            can_review = True
            
    attributes_data = OrderedDict()
    for variant in variants:
        for attr_value in variant.attributes.all():
            attr_name = attr_value.attribute.name
            if attr_name not in attributes_data:
                attributes_data[attr_name] = set()
            attributes_data[attr_name].add(attr_value)
    for attr_name in attributes_data:
        attributes_data[attr_name] = sorted(list(attributes_data[attr_name]), key=lambda x: x.value)

    variant_map = {
        "-".join(str(a.id) for a in v.attributes.all().order_by('id')): {
            'id': v.id,
            'price': f"{v.get_best_offer().price:.2f}" if v.get_best_offer() else None,
            'in_stock': v.get_best_offer().quantity > 0 if v.get_best_offer() else False,
            'image_urls': [img.image.url for img in v.images.all()],
        } for v in variants
    }

    context = {
        'product': product,
        'main_offer': variants.first().get_best_offer() if variants and variants.first().offers.exists() else None,
        'parent_images': parent_images,
        'attributes_data': attributes_data,
        'variant_map_json': json.dumps(variant_map),
        'reviews': reviews,
        'can_review': can_review,
        'questions': questions,
        'question_form': question_form,
    }
    return render(request, 'products/product_detail.html', context)


def get_variant_data_api(request, variant_id):
    """
    An API endpoint that returns JSON data for a specific product variant's best offer and images.
    """
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


# --- SELLER PRODUCT REQUEST VIEW ---
@login_required
@seller_required
def request_new_product_view(request):
    """
    Allows a seller to fill out a form to request a new product be added to the catalog.
    """
    if request.method == 'POST':
        form = ProductRequestForm(request.POST)
        if form.is_valid():
            product_request = form.save(commit=False)
            product_request.seller = request.user.seller # Assign the logged-in seller
            product_request.save()
            messages.success(request, "Your product request has been submitted for review. Thank you!")
            return redirect('marketplace:seller_dashboard')
    else:
        form = ProductRequestForm()

    context = {
        'form': form
    }
    return render(request, 'products/product_request_form.html', context)
