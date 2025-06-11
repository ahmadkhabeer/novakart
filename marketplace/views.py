from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db.models import Q

from .models import Seller, Offer
from products.models import ProductVariant # We need this for the search
from .forms import SellerRegisterForm, OfferForm
from .decorators import seller_required

@login_required
def seller_register_view(request):
    # ... (this view is correct and remains unchanged)
    if Seller.objects.filter(user=request.user).exists():
        messages.info(request, "You are already registered as a seller.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            try:
                sellers_group = Group.objects.get(name='Sellers')
            except Group.DoesNotExist:
                messages.error(request, "A critical error occurred: The 'Sellers' user group does not exist. Please contact support.")
                return redirect('core:product_list')

            seller = form.save(commit=False)
            seller.user = request.user
            seller.save()
            request.user.groups.add(sellers_group)
            messages.success(request, "Congratulations! You are now registered as a seller on NovaKart.")
            return redirect('users:dashboard')
    else:
        form = SellerRegisterForm()

    context = {'form': form}
    return render(request, 'marketplace/seller_register.html', context)


@login_required
@seller_required
def seller_dashboard_view(request):
    # ... (this view is correct and remains unchanged)
    seller = request.user.seller
    offers = Offer.objects.filter(seller=seller).select_related('variant__parent_product')
    context = {
        'seller': seller,
        'offers': offers,
        'offer_count': offers.count(),
    }
    return render(request, 'marketplace/seller_dashboard.html', context)


# --- NEW VIEWS FOR CREATING OFFERS ---

@login_required
@seller_required
def offer_create_product_select_view(request):
    """
    Step 1 of creating an offer: Search for and select a product variant.
    """
    query = request.GET.get('q')
    variants = None
    if query:
        # Search for variants based on product title, brand, or ASINs
        variants = ProductVariant.objects.filter(
            Q(parent_product__title__icontains=query) |
            Q(parent_product__brand__icontains=query) |
            Q(parent_product__parent_asin__iexact=query) |
            Q(child_asin__iexact=query)
        ).select_related('parent_product')
    
    context = {
        'variants': variants,
        'query': query
    }
    return render(request, 'marketplace/offer_product_select.html', context)

@login_required
@seller_required
def offer_create_view(request, variant_id):
    """
    Step 2 of creating an offer: Fill out the offer details for the selected variant.
    """
    variant = get_object_or_404(ProductVariant, id=variant_id)
    seller = request.user.seller

    # Check if this seller already has an offer for this variant
    if Offer.objects.filter(variant=variant, seller=seller).exists():
        messages.warning(request, "You already have an active offer for this product. Please edit the existing offer instead.")
        return redirect('marketplace:seller_dashboard')

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.seller = seller
            offer.variant = variant
            offer.save()
            messages.success(request, f"Your offer for '{variant.parent_product.title}' has been successfully created.")
            return redirect('marketplace:seller_dashboard')
    else:
        form = OfferForm()

    context = {
        'form': form,
        'variant': variant
    }
    return render(request, 'marketplace/offer_form.html', context)
