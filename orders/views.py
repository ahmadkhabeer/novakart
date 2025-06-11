from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from .forms import ShippingAddressSelectForm, PaymentMethodSelectForm, PromotionApplyForm
from carts.models import Cart
from .models import Order, OrderItem, Shipment
from promotions.models import Promotion # Import the Promotion model

@login_required
def checkout_view(request):
    """
    Displays the checkout page with forms for shipping, payment, and promotions.
    """
    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('carts:view_cart')

    # Instantiate the forms, passing the current user to populate their data.
    shipping_form = ShippingAddressSelectForm(user=request.user)
    payment_form = PaymentMethodSelectForm(user=request.user)
    promo_form = PromotionApplyForm() # This form doesn't need initial data.

    subtotal = sum(item.get_total_price() for item in active_items)

    context = {
        'cart_items': active_items,
        'subtotal': subtotal,
        'shipping_form': shipping_form,
        'payment_form': payment_form,
        'promo_form': promo_form,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@transaction.atomic # This ensures all database operations are completed or none are.
def place_order_view(request):
    """
    Handles the submission of the checkout form and creates the final order.
    """
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.error(request, "Cannot place an order with an empty cart.")
        return redirect('carts:view_cart')

    # Bind POST data to the forms
    shipping_form = ShippingAddressSelectForm(request.POST, user=request.user)
    payment_form = PaymentMethodSelectForm(request.POST, user=request.user)
    promo_form = PromotionApplyForm(request.POST)

    if not all([shipping_form.is_valid(), payment_form.is_valid(), promo_form.is_valid()]):
        messages.error(request, "There was an error with your selections. Please try again.")
        # Re-render the checkout page with validation errors (a more advanced implementation).
        return redirect('orders:checkout')
        
    shipping_address = shipping_form.cleaned_data['shipping_address']
    payment_method = payment_form.cleaned_data['payment_method']
    promo_code = promo_form.cleaned_data.get('promo_code') # This is a Promotion object or None.

    # --- 1. Calculate final total (including promotions) ---
    subtotal = sum(item.get_total_price() for item in active_items)
    final_total = subtotal
    # In a real scenario, you would calculate the discount from the promo_code here.
    # For now, we will just record the subtotal.
    
    # --- 2. Payment Gateway Logic (Placeholder) ---
    # In a real application, this is where you would call Stripe, PayPal, etc.
    # You would pass the `final_total` and a token from the `payment_method`.
    # payment_successful = payment_gateway.charge(token=payment_method.token, amount=final_total)
    # For this guide, we will assume the payment is always successful.
    payment_successful = True

    if not payment_successful:
        messages.error(request, "Payment failed. Please try again or use a different payment method.")
        return redirect('orders:checkout')

    # --- 3. Create the Order and related objects ---
    # Create the main Order object
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_paid=final_total, # Store the final calculated price
        paid=True,
    )
    if promo_code:
        order.promotions_applied.add(promo_code)

    # Move items from cart to order and group them by seller for shipment creation
    items_by_seller = {}
    for item in active_items:
        order_item = OrderItem.objects.create(
            order=order,
            offer=item.offer,
            price_at_purchase=item.offer.price, # Freeze the price
            quantity=item.quantity
        )
        # Reduce stock quantity for the offer
        item.offer.quantity -= item.quantity
        item.offer.save()
        
        # Group order items by seller
        seller = item.offer.seller
        if seller not in items_by_seller:
            items_by_seller[seller] = []
        items_by_seller[seller].append(order_item)

    # Create a separate Shipment for each seller in the order
    for seller, items in items_by_seller.items():
        shipment = Shipment.objects.create(
            order=order,
            seller=seller
        )
        shipment.items.set(items)

    # --- 4. Clean up ---
    # Clear the active items from the user's cart
    active_items.delete()

    messages.success(request, f"Thank you! Your order #{order.id} has been placed.")
    return redirect('orders:order_success', order_id=order.id)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})
