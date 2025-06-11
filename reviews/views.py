from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductReview
from products.models import Product
from orders.models import OrderItem
from .forms import ProductReviewForm

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Check if the user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        offer__variant__parent_product=product
    ).exists()

    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect(product.get_absolute_url())
    
    # Check if the user has already reviewed this product
    if ProductReview.objects.filter(customer=request.user, product=product).exists():
        messages.info(request, "You have already reviewed this product.")
        return redirect(product.get_absolute_url())

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.verified_purchase = True
            review.save()
            messages.success(request, "Your review has been submitted.")
            return redirect(product.get_absolute_url())
    else:
        form = ProductReviewForm()

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'reviews/add_review.html', context)
