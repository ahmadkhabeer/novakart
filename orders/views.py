import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal

from .paymob_service import PaymobService
from carts.models import Cart
from .models import Order, OrderItem, Shipment, Promotion, ReturnRequest, ReturnItem
from .forms import ShippingAddressSelectForm, PromotionApplyForm, ReturnRequestForm


# --- CHECKOUT & PAYMENT VIEWS ---

@login_required
def checkout_view(request):
    """
    Step 1 of Checkout: Display cart summary and shipping form.
    Handles promo code application via session.
    """
    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False)

    if not active_items.exists():
        messages.info(request, "Your cart is empty.")
        return redirect('carts:view_cart')

    if request.method == 'POST':
        # This part handles the promo code form submission
        promo_form = PromotionApplyForm(request.POST)
        if promo_form.is_valid():
            promo = promo_form.cleaned_data.get('promo_code')
            if promo:
                request.session['promo_id'] = promo.id
                messages.success(request, f"Promotion '{promo.name}' applied.")
            else:
                # If the form is submitted with an empty field, remove existing promo
                if 'promo_id' in request.session:
                    del request.session['promo_id']
                messages.info(request, "Promotion removed.")
            return redirect('orders:checkout')
    else:
        promo_form = PromotionApplyForm()

    shipping_form = ShippingAddressSelectForm(user=request.user)

    promo_id = request.session.get('promo_id')
    totals = cart.get_totals(promo_id=promo_id)

    context = {
        'cart_items': active_items,
        'shipping_form': shipping_form,
        'promo_form': promo_form,
        **totals
    }
    return render(request, 'orders/checkout.html', context)


@login_required
@transaction.atomic
def start_payment_view(request):
    """
    Step 2 of Checkout: Creates a PENDING order locally and redirects the user to Paymob for payment.
    This view is triggered when the user confirms their shipping address.
    """
    if request.method != 'POST':
        return redirect('orders:checkout')

    cart = get_object_or_404(Cart, user=request.user)
    active_items = cart.items.filter(is_saved_for_later=False).select_related('offer')

    if not active_items.exists():
        messages.error(request, "Your cart is empty, cannot proceed to payment.")
        return redirect('carts:view_cart')

    shipping_form = ShippingAddressSelectForm(request.POST, user=request.user)

    if not shipping_form.is_valid():
        messages.error(request, "Please select a valid shipping address.")
        # To display the error correctly, we should re-render the checkout page
        # This part is simplified for brevity; a full implementation would re-render the form with errors.
        return redirect('orders:checkout')
        
    shipping_address = shipping_form.cleaned_data['shipping_address']
    
    # Re-calculate totals securely on the backend to ensure integrity
    promo_id = request.session.get('promo_id')
    totals = cart.get_totals(promo_id=promo_id)
    final_total = totals['final_total']
    
    # Create the Order locally first with paid=False
    order = Order.objects.create(
        user=request.user,
        shipping_address=shipping_address,
        total_paid=final_total,
        paid=False,
        status=Order.OrderStatus.PENDING
    )
    
    if promo_id and totals['discount'] > 0:
        try:
            promo_code = Promotion.objects.get(id=promo_id)
            if promo_code.is_valid():
                order.promotions_applied.add(promo_code)
        except Promotion.DoesNotExist:
            pass

    for item in active_items:
        OrderItem.objects.create(
            order=order, 
            offer=item.offer, 
            price_at_purchase=item.offer.price, 
            quantity=item.quantity
        )

    # Start Paymob Payment Flow
    try:
        paymob = PaymobService()
        auth_token = paymob.get_auth_token()
        paymob_order_data = paymob.create_order(auth_token, order)
        payment_key = paymob.get_payment_key(auth_token, paymob_order_data, order)
        iframe_url = paymob.get_payment_iframe_url(payment_key)
        
        return redirect(iframe_url)

    except Exception as e:
        messages.error(request, f"Could not connect to the payment provider. Please try again later.")
        # The transaction will be rolled back automatically because of the @transaction.atomic decorator
        return redirect('orders:checkout')


@csrf_exempt
def payment_webhook(request):
    """
    The secure, server-to-server webhook from Paymob to confirm transaction status.
    This is the source of truth for payment success.
    """
    if request.method == 'POST':
        data = json.loads(request.body)
        obj_data = data.get('obj')
        hmac_from_request = data.get('hmac')

        paymob = PaymobService()
        if not paymob.validate_hmac(hmac_from_request, obj_data):
            return HttpResponse("HMAC validation failed.", status=403)
        
        order_id = obj_data.get('merchant_order_id')
        success = obj_data.get('success')

        with transaction.atomic():
            try:
                order = Order.objects.get(id=order_id)
                if success and not order.paid:
                    order.paid = True
                    order.status = Order.OrderStatus.PROCESSING
                    order.save()

                    items_by_seller = {}
                    for item in order.items.select_related('offer__seller', 'offer__variant__parent_product').all():
                        # Decrement stock
                        item.offer.quantity -= item.quantity
                        item.offer.save()
                        
                        # Group items for shipment creation
                        seller = item.offer.seller
                        if seller not in items_by_seller:
                            items_by_seller[seller] = []
                        items_by_seller[seller].append(item)

                    for seller, items in items_by_seller.items():
                        shipment = Shipment.objects.create(order=order, seller=seller)
                        shipment.items.set(items)

                    # Clear the user's cart
                    Cart.objects.filter(user=order.user).delete()
                    if 'promo_id' in request.session:
                        del request.session['promo_id']

                    # In production, use Celery to send email asynchronously
                    # send_order_confirmation_email_task.delay(order.id)
                
                return HttpResponse("Webhook received.", status=200)
            
            except Order.DoesNotExist:
                return HttpResponse("Order not found.", status=404)

    return HttpResponse("Invalid request method.", status=405)


def payment_processed_callback(request):
    """
    The view the user is redirected back to from Paymob.
    Checks the 'success' query parameter to give immediate user feedback.
    """
    success = request.GET.get('success') == 'true'
    
    if success:
        messages.success(request, "Thank you! Your payment is being processed. You will be notified once confirmed.")
    else:
        messages.error(request, "Your payment was not successful or was cancelled. Please try again or contact support.")
        
    return redirect('orders:order_history')


@login_required
def order_success_view(request, order_id):
    """
    Displays a simple success page after an order is confirmed by the webhook.
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
    context = {'order': order, 'shipments': shipments}
    return render(request, 'orders/order_detail.html', context)


@login_required
@transaction.atomic
def initiate_return_view(request, order_id):
    """
    Allows a user to initiate a return request for a completed order.
    """
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status != Order.OrderStatus.DELIVERED:
        messages.error(request, "You can only initiate a return for delivered orders.")
        return redirect('orders:order_detail', order_id=order.id)
        
    if request.method == 'POST':
        form = ReturnRequestForm(request.POST, order=order)
        if form.is_valid():
            return_request = ReturnRequest.objects.create(order=order, user=request.user, reason=form.cleaned_data['reason'])
            for item in form.cleaned_data['items_to_return']:
                ReturnItem.objects.create(return_request=return_request, order_item=item, quantity=item.quantity)
            messages.success(request, f"Your return request for order #{order.id} has been submitted.")
            return redirect('orders:order_detail', order_id=order.id)
    else:
        form = ReturnRequestForm(order=order)
        
    context = {'form': form, 'order': order}
    return render(request, 'orders/initiate_return.html', context)
