from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.template.loader import render_to_string
from decimal import Decimal

from .forms import ShippingAddressSelectForm, PaymentMethodSelectForm, PromotionApplyForm, ReturnRequestForm
from carts.models import Cart
from .models import Order, OrderItem, Shipment, Promotion, ReturnRequest, ReturnItem

def send_order_confirmation_email(order):
    """
    Helper function to send an order confirmation email to the user.
    """
    subject = f"Your NovaKart Order Confirmation #{order.id}"
    html_message = render_to_string('emails/order_confirmation.html', {'order': order})
    plain_message = f"Your order #{order.id} has been placed successfully."
    try:
        send_mail(subject, plain_message, 'noreply@novakart.com', [order.user.email], html_message=html_message)
    except Exception as e:
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

    if request.method == 'POST':
        promo_form = PromotionApplyForm(request.POST)
        if promo_form.is_valid():
            promo = promo_form.cleaned_data['promo_code']
            request.session['promo_id'] = promo.id
            messages.success(request, f"Promotion '{promo.name}' applied.")
            return redirect('orders:checkout')
    else:
        promo_form = PromotionApplyForm()

    shipping_form = ShippingAddressSelectForm(user=request.user)
    payment_form = PaymentMethodSelectForm(user=request.user)

    promo_id = request.session.get('promo_id')
    totals = cart.get_totals(promo_id=promo_id)

    context = {
        'cart_items': active_items,
        'shipping_form': shipping_form,
        'payment_form': payment_form,
        'promo_form': promo_form,
        **totals
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@transaction.atomic
def place_order_view(request):
    """
    Handles the submission of the checkout form and creates the final order.
    """
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False).select_related('offer')

    if not active_items.exists():
        messages.error(request, "Cannot place an order with an empty cart.")
        return redirect('carts:view_cart')

    for item in active_items:
        if item.quantity > item.offer.quantity:
            messages.error(request, f"Sorry, the quantity for '{item.offer.variant.parent_product.title}' has changed. Only {item.offer.quantity} are left in stock. Please update your cart.")
            return redirect('carts:view_cart')

    shipping_form = ShippingAddressSelectForm(request.POST, user=request.user)
    payment_form = PaymentMethodSelectForm(request.POST, user=request.user)

    if not all([shipping_form.is_valid(), payment_form.is_valid()]):
        messages.error(request, "Please select a valid shipping address and payment method.")
        return redirect('orders:checkout')
        
    shipping_address = shipping_form.cleaned_data['shipping_address']
    
    promo_id = request.session.get('promo_id')
    totals = cart.get_totals(promo_id=promo_id)
    final_total = totals['final_total']
    
    promo_code = None
    if promo_id:
        try:
            promo_code = Promotion.objects.get(id=promo_id)
            if not promo_code.is_valid():
                promo_code = None
        except Promotion.DoesNotExist:
            promo_code = None

    payment_successful = True

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
    
    # In a real production app, this would be an asynchronous task
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
    shipments = order.shipments.prefetch_related('items__offer__variant__parent_product', 'seller').all()
    
    context = {
        'order': order,
        'shipments': shipments,
    }
    return render(request, 'orders/order_detail.html', context)

# --- NEW CUSTOMER RETURNS VIEW ---
@login_required
@transaction.atomic
def initiate_return_view(request, order_id):
    """
    Allows a user to initiate a return request for a completed order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Business logic: Only allow returns for orders that are 'DELIVERED'.
    # In a real app, you might also check if a return period (e.g., 30 days) has passed.
    if order.status != Order.OrderStatus.DELIVERED:
        messages.error(request, "You can only initiate a return for delivered orders.")
        return redirect('orders:order_detail', order_id=order.id)

    if request.method == 'POST':
        form = ReturnRequestForm(request.POST, order=order)
        if form.is_valid():
            # Create the main ReturnRequest object
            return_request = ReturnRequest.objects.create(
                order=order,
                user=request.user,
                reason=form.cleaned_data['reason']
            )
            # Create a ReturnItem for each OrderItem selected in the form
            for item in form.cleaned_data['items_to_return']:
                ReturnItem.objects.create(
                    return_request=return_request,
                    order_item=item,
                    quantity=item.quantity # Assuming return of full quantity for simplicity
                )
            
            messages.success(request, f"Your return request for order #{order.id} has been submitted.")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = ReturnRequestForm(order=order)

    context = {
        'form': form,
        'order': order
    }
    return render(request, 'orders/initiate_return.html', context)
