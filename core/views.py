from django.shortcuts import render, get_object_or_404
from products.models import Product, BrowseNode
from marketplace.models import Offer
from django.db.models import OuterRef, Subquery

def product_list(request, category_slug=None):
    nodes = BrowseNode.objects.filter(parent__isnull=True)
    products = Product.objects.filter(is_variation_parent=True)

    # --- PERFORMANCE OPTIMIZATION ---
    # Create a subquery to find the minimum price for any active offer related to a product.
    # This avoids running a separate query for every product in the template.
    best_offer_price = Offer.objects.filter(
        variant__parent_product=OuterRef('pk'), 
        is_active=True
    ).order_by('price').values('price')[:1]

    # Annotate each product with its best offer price.
    products = products.annotate(
        best_price=Subquery(best_offer_price)
    )
    # --- END OPTIMIZATION ---

    current_node = None
    if category_slug:
        current_node = get_object_or_404(BrowseNode, slug=category_slug)
        products = products.filter(browse_nodes=current_node)

    context = {
        'nodes': nodes,
        'products': products,
        'current_node': current_node
    }
    return render(request, 'core/product_list.html', context)

def product_detail(request, parent_asin):
    """
    Displays the details for a parent product, its variants, and offers.
    """
    product = get_object_or_404(Product, parent_asin=parent_asin, is_variation_parent=True)
    
    # Get all variants and prefetch their offers and attributes for efficiency.
    variants = product.variants.prefetch_related(
        'offers__seller', 
        'attributes__attribute_value__attribute'
    ).all()
    
    main_offer = None
    if variants and variants.first().offers.exists():
        main_offer = variants.first().offers.order_by('price').first()

    context = {
        'product': product,
        'variants': variants,
        'main_offer': main_offer,
    }
    return render(request, 'core/product_detail.html', context)
