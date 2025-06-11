from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decimal import Decimal

from .forms import ShippingAddressSelectForm, PaymentMethodSelectForm, PromotionApplyForm
from carts.models import Cart
from .models import Order, OrderItem, Shipment, Promotion

def send_order_confirmation_email(order):
    subject = f"Your NovaKart Order Confirmation #{order.id}"
    html_message = render_to_string('emails/order_confirmation.html', {'order': order})
    plain_message = f"Your order #{order.id} has been placed successfully."
    try:
        send_mail(subject, plain_message, 'noreply@novakart.com', [order.user.email], html_message=html_message)
    except Exception as e:
        print(f"Error sending email for order {order.id}: {e}")

@login_required
def checkout_view(request):
    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('carts:view_cart')

    # Handle promo code application if the form is submitted
    if request.method == 'POST':
        promo_form = PromotionApplyForm(request.POST)
        if promo_form.is_valid():
            promo = promo_form.cleaned_data['promo_code']
            # Store the valid promo code ID in the session
            request.session['promo_id'] = promo.id
            messages.success(request, f"Promotion '{promo.name}' applied.")
            return redirect('orders:checkout')
    else:
        promo_form = PromotionApplyForm()

    shipping_form = ShippingAddressSelectForm(user=request.user)
    payment_form = PaymentMethodSelectForm(user=request.user)

    subtotal = sum(item.get_total_price() for item in active_items)
    discount = Decimal('0.00')
    promo_id = request.session.get('promo_id')

    if promo_id:
        try:
            promo = Promotion.objects.get(id=promo_id)
            if promo.is_valid():
                if promo.discount_type == Promotion.DiscountType.PERCENTAGE:
                    discount = (subtotal * (promo.value / 100)).quantize(Decimal('0.01'))
                else: # Fixed amount
                    discount = promo.value
            else:
                # Clear invalid promo from session
                del request.session['promo_id']
        except Promotion.DoesNotExist:
            del request.session['promo_id']

    final_total = subtotal - discount

    context = {
        'cart_items': active_items,
        'subtotal': subtotal,
        'discount': discount,
        'final_total': final_total,
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

    if not all([shipping_form.is_valid(), payment_form.is_valid()]):
        messages.error(request, "Please select a valid shipping address and payment method.")
        return redirect('orders:checkout')
        
    shipping_address = shipping_form.cleaned_data['shipping_address']
    
    # Recalculate total and discount to ensure integrity
    subtotal = sum(item.get_total_price() for item in active_items)
    discount = Decimal('0.00')
    promo_id = request.session.get('promo_id')
    promo_code = None
    if promo_id:
        try:
            promo_code = Promotion.objects.get(id=promo_id)
            if promo_code.is_valid():
                if promo_code.discount_type == Promotion.DiscountType.PERCENTAGE:
                    discount = (subtotal * (promo_code.value / 100)).quantize(Decimal('0.01'))
                else:
                    discount = promo_code.value
        except Promotion.DoesNotExist:
            promo_code = None

    final_total = subtotal - discount

    payment_successful = True # Placeholder for payment gateway call

    if not payment_successful:
        messages.error(request, "Payment failed.")
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
    if 'promo_id' in request.session:
        del request.session['promo_id']
    
    send_order_confirmation_email(order)

    messages.success(request, f"Thank you! Your order #{order.id} has been placed.")
    return redirect('orders:order_success', order_id=order.id)


@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_history_view(request):
    # PERFORMANCE OPTIMIZATION: Use select_related to also fetch shipping address in one query
    orders = Order.objects.filter(user=request.user).select_related('shipping_address').order_by('-created_at')
    context = {'orders': orders}
    return render(request, 'orders/order_history.html', context)


@login_required
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    # PERFORMANCE OPTIMIZATION: Prefetch all related data needed for the template in efficient queries
    shipments = order.shipments.prefetch_related('items__offer__variant__parent_product', 'seller').all()
    
    context = {
        'order': order,
        'shipments': shipments,
    }
    return render(request, 'orders/order_detail.html', context)
