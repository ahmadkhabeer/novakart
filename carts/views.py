from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from marketplace.models import Offer
from .models import Cart, CartItem

# --- Helper Function ---

def _get_cart(request):
    """
    A private helper function to retrieve the current user's or guest's cart.
    Creates a cart if one doesn't exist for the session or user.
    """
    if request.user.is_authenticated:
        # For logged-in users, get or create their cart.
        cart, created = Cart.objects.get_or_create(user=request.user)
        # If the user also had a session cart, you might want to merge it here.
        # This is a more complex feature for a later stage.
    else:
        # For guests, use the session key.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart

# --- Main Cart View ---

def view_cart(request):
    """
    Displays the user's shopping cart with active and saved-for-later items.
    """
    cart = _get_cart(request)
    
    # Separate items into active and saved lists for easy rendering in the template.
    active_items = cart.items.filter(is_saved_for_later=False)
    saved_items = cart.items.filter(is_saved_for_later=True)
    
    # Calculate subtotal only for active items.
    subtotal = sum(item.get_total_price() for item in active_items)
    
    context = {
        'cart': cart,
        'active_items': active_items,
        'saved_items': saved_items,
        'subtotal': subtotal,
    }
    return render(request, 'carts/view_cart.html', context)

# --- Cart Action Views ---

@require_POST
def add_to_cart(request):
    """
    Adds an item to the cart or updates its quantity.
    """
    cart = _get_cart(request)
    offer_id = request.POST.get('offer_id')
    quantity = int(request.POST.get('quantity', 1))

    if not offer_id:
        messages.error(request, "Invalid request: Offer not specified.")
        return redirect('core:product_list')

    offer = get_object_or_404(Offer, id=offer_id)
    
    # Get or create the cart item, ensuring it's not in the "saved for later" state.
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        offer=offer, 
        defaults={'quantity': 0, 'is_saved_for_later': False}
    )
    
    # If the item was previously saved for later, move it back to the active cart.
    if cart_item.is_saved_for_later:
        cart_item.is_saved_for_later = False
        cart_item.quantity = 0 # Reset quantity when moving from saved list

    # Check against available stock
    new_quantity = cart_item.quantity + quantity
    if new_quantity > offer.quantity:
        messages.warning(request, f"Only {offer.quantity} items are in stock. Your quantity has been adjusted.")
        cart_item.quantity = offer.quantity
    else:
        cart_item.quantity = new_quantity
    
    cart_item.save()
    messages.success(request, f"Added '{offer.variant.parent_product.title}' to your cart.")
    
    return redirect('carts:view_cart')

@require_POST
def update_cart_item(request, item_id):
    """
    Updates the quantity of a specific item in the cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))

    # Ensure the user is updating an item in their own cart.
    if _get_cart(request) != cart_item.cart:
        messages.error(request, "You do not have permission to do that.")
        return redirect('carts:view_cart')
    
    if quantity > 0:
        if quantity > cart_item.offer.quantity:
            messages.warning(request, f"Quantity adjusted to available stock ({cart_item.offer.quantity}).")
            cart_item.quantity = cart_item.offer.quantity
        else:
            cart_item.quantity = quantity
            messages.success(request, "Cart updated.")
        cart_item.save()
    else:
        # If quantity is 0 or less, remove the item.
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect('carts:view_cart')

@require_POST
def remove_from_cart(request, item_id):
    """
    Removes an item completely from the cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)

    if _get_cart(request) == cart_item.cart:
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")
    else:
        messages.error(request, "You do not have permission to do that.")

    return redirect('carts:view_cart')

@require_POST
def save_for_later(request, item_id):
    """
    Moves an item from the active cart to the 'Saved for Later' list.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    if _get_cart(request) == cart_item.cart:
        cart_item.is_saved_for_later = True
        cart_item.save()
        messages.success(request, "Item saved for later.")
    else:
        messages.error(request, "You do not have permission to do that.")
    return redirect('carts:view_cart')

@require_POST
def move_to_cart(request, item_id):
    """

    Moves a 'Saved for Later' item back to the active cart.
    """
    cart_item = get_object_or_404(CartItem, id=item_id)
    if _get_cart(request) == cart_item.cart:
        cart_item.is_saved_for_later = False
        cart_item.save()
        messages.success(request, "Item moved to your cart.")
    else:
        messages.error(request, "You do not have permission to do that.")
    return redirect('carts:view_cart')
