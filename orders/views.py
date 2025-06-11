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
    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('carts:view_cart')

    shipping_form = ShippingAddressSelectForm(user=request.user)
    payment_form = PaymentMethodSelectForm(user=request.user)
    promo_form = PromotionApplyForm()

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
@transaction.atomic
def place_order_view(request):
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.error(request, "Cannot place an order with an empty cart.")
        return redirect('carts:view_cart')

    shipping_form = ShippingAddressSelectForm(request.POST, user=request.user)
    payment_form = PaymentMethodSelectForm(request.POST, user=request.user)
    promo_form = PromotionApplyForm(request.POST)

    # --- UPDATED: FORM ERROR HANDLING ---
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
    promo_code = promo_form.cleaned_data.get('promo_code')

    subtotal = sum(item.get_total_price() for item in active_items)
    final_total = subtotal
    
    payment_successful = True # Placeholder for payment gateway call

    if not payment_successful:
        messages.error(request, "Payment failed. Please try again.")
        return redirect('orders:checkout')

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
        item.offer.quantity -= item.quantity
        item.offer.save()
        
        seller = item.offer.seller
        if seller not in items_by_seller:
            items_by_seller[seller] = []
        items_by_seller[seller].append(order_item)

    for seller, items in items_by_seller.items():
        shipment = Shipment.objects.create(order=order, seller=seller)
        shipment.items.set(items)

    active_items.delete()
    
    # Send the confirmation email
    send_order_confirmation_email(order)

    messages.success(request, f"Thank you! Your order #{order.id} has been placed.")
    return redirect('orders:order_success', order_id=order.id)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})
