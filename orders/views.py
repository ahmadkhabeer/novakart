from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string

from .forms import ShippingAddressSelectForm, PaymentMethodSelectForm, PromotionApplyForm
from carts.models import Cart
from .models import Order, OrderItem, Shipment

def send_order_confirmation_email(order):
    """
    Helper function to send an order confirmation email to the user.
    """
    subject = f"Your NovaKart Order Confirmation #{order.id}"
    html_message = render_to_string('emails/order_confirmation.html', {'order': order})
    plain_message = f"Your order #{order.id} has been placed successfully." # Fallback plain text
    try:
        send_mail(subject, plain_message, 'noreply@novakart.com', [order.user.email], html_message=html_message)
    except Exception as e:
        # In production, you would log this error.
        print(f"Error sending email for order {order.id}: {e}")

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
        messages.error(request, "There was an error with your selections. Please review the fields below.")
        
        # Re-render the checkout page with the invalid forms so the user can see the errors.
        context = {
            'cart_items': active_items,
            'subtotal': sum(item.get_total_price() for item in active_items),
            'shipping_form': shipping_form,
            'payment_form': payment_form,
            'promo_form': promo_form,
        }
        return render(request, 'orders/checkout.html', context)
        
    shipping_address = shipping_form.cleaned_data['shipping_address']
    payment_method = payment_form.cleaned_data['payment_method']
    promo_code = promo_form.cleaned_data.get('promo_code') # This is a Promotion object or None.

    # 1. Calculate final total (including promotions)
    subtotal = sum(item.get_total_price() for item in active_items)
    final_total = subtotal
    
    # 2. Payment Gateway Logic (Placeholder)
    payment_successful = True # Assume payment is always successful.

    if not payment_successful:
        messages.error(request, "Payment failed. Please try again or use a different payment method.")
        return redirect('orders:checkout')

    # 3. Create the Order and related objects
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_paid=final_total,
        paid=True,
    )
    if promo_code:
        order.promotions_applied.add(promo_code)

    items_by_seller = {}
    for item in active_items:
        order_item = OrderItem.objects.create(
            order=order,
            offer=item.offer,
            price_at_purchase=item.offer.price,
            quantity=item.quantity
        )
        # Reduce stock quantity for the offer
        item.offer.quantity -= item.quantity
        item.offer.save()
        
        seller = item.offer.seller
        if seller not in items_by_seller:
            items_by_seller[seller] = []
        items_by_seller[seller].append(order_item)

    # Create a separate Shipment for each seller in the order
    for seller, items in items_by_seller.items():
        shipment = Shipment.objects.create(order=order, seller=seller)
        shipment.items.set(items)

    # 4. Clean up
    active_items.delete()
    
    # 5. Send confirmation email
    send_order_confirmation_email(order)

    messages.success(request, f"Thank you! Your order #{order.id} has been placed.")
    return redirect('orders:order_success', order_id=order.id)


@login_required
def order_success_view(request, order_id):
    """
    Displays a simple success page after an order is placed.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    """
    Displays a list of all past orders for the logged-in user.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail_view(request, order_id):
    """
    Displays the detailed information for a single order, including its shipments.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # Prefetch related items for performance
    order_items = order.items.prefetch_related('offer__variant__parent_product').all()
    shipments = order.shipments.prefetch_related('items__offer__variant__parent_product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
        'shipments': shipments,
    }
    return render(request, 'orders/order_detail.html', context)
