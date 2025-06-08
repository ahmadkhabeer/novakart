from django.shortcuts import render
from products.models import Product, BrowseNode

def product_list(request, category_slug=None):
    nodes = BrowseNode.objects.filter(parent__isnull=True) # Top-level categories
    products = Product.objects.filter(is_variation_parent=True)

    current_node = None
    if category_slug:
        # This logic needs to be expanded to handle nested categories
        current_node = BrowseNode.objects.get(slug=category_slug)
        products = products.filter(browse_nodes=current_node)

    context = {
        'nodes': nodes,
        'products': products,
        'current_node': current_node
    }
    return render(request, 'core/product_list.html', context)
