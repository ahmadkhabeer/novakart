from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from marketplace.models import Offer
from .models import Cart, CartItem

# --- Helper Function ---

def _get_cart(request):
    """
    A private helper function to retrieve the cart, handling guest-to-user cart merging.
    """
    if request.user.is_authenticated:
        # Get the permanent cart associated with the user.
        user_cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if there was a cart in the session from when the user was a guest.
        session_key = request.session.get('cart_session_key')
        if session_key:
            try:
                guest_cart = Cart.objects.get(session_key=session_key, user=None)
                # If a guest cart exists, merge its items into the user's cart.
                for item in guest_cart.items.all():
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=user_cart, 
                        offer=item.offer,
                        defaults={'quantity': item.quantity}
                    )
                    if not item_created:
                        # If item already existed in the user's cart, add quantities.
                        cart_item.quantity += item.quantity
                        cart_item.save()
                
                # The guest cart has been merged, so it can be deleted.
                guest_cart.delete()
                # Clear the session key.
                del request.session['cart_session_key']

            except Cart.DoesNotExist:
                # The session key was invalid or the cart was already handled.
                pass
        
        return user_cart
    
    else:
        # For guests, use the session key.
        session_key = request.session.get('cart_session_key')
        if not session_key:
            request.session.create()
            # We store the key in the session to remember it.
            request.session['cart_session_key'] = request.session.session_key
            session_key = request.session.session_key
            
        cart, created = Cart.objects.get_or_create(session_key=session_key, user=None)
        return cart

# --- Main Cart View ---

def view_cart(request):
    """
    Displays the user's shopping cart with active and saved-for-later items.
    """
    cart = _get_cart(request)
    active_items = cart.items.filter(is_saved_for_later=False)
    saved_items = cart.items.filter(is_saved_for_later=True)
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
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, 
        offer=offer, 
        defaults={'quantity': 0, 'is_saved_for_later': False}
    )
    
    if cart_item.is_saved_for_later:
        cart_item.is_saved_for_later = False
        cart_item.quantity = 0

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
