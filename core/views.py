from django.shortcuts import render, get_object_or_404
from products.models import Product, BrowseNode
from marketplace.models import Offer
from django.db.models import OuterRef, Subquery, Q
from .forms import ProductFilterForm

def product_list(request, category_slug=None):
    nodes = BrowseNode.objects.filter(parent__isnull=True)
    
    # Start with the base queryset
    products_qs = Product.objects.filter(is_variation_parent=True)

    form = ProductFilterForm(request.GET)
    if form.is_valid():
        query = form.cleaned_data.get('q')
        sort_by = form.cleaned_data.get('sort_by')

        if query:
            products_qs = products_qs.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(brand__icontains=query)
            )

    best_offer_price = Offer.objects.filter(
        variant__parent_product=OuterRef('pk'),
        is_active=True
    ).order_by('price').values('price')[:1]
    
    # --- THIS IS THE FIX ---
    # We annotate the price AND prefetch the related images in an efficient way.
    products = products_qs.annotate(
        best_price=Subquery(best_offer_price)
    ).prefetch_related('images')
    # --- END FIX ---

    if 'sort_by' in locals() and sort_by:
        if sort_by == 'price_asc':
            products = products.order_by('best_price')
        elif sort_by == 'price_desc':
            products = products.order_by('-best_price')
        elif sort_by == 'name_asc':
            products = products.order_by('title')
        elif sort_by == 'name_desc':
            products = products.order_by('-title')

    current_node = None
    if category_slug:
        current_node = get_object_or_404(BrowseNode, slug=category_slug)
        products = products.filter(browse_nodes=current_node)

    context = {
        'nodes': nodes,
        'products': products,
        'current_node': current_node,
        'filter_form': form,
    }
    return render(request, 'core/product_list.html', context)
