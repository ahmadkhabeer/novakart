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

    # 1. Check if the user has purchased this product
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        offer__variant__parent_product=product,
        order__paid=True # Only allow reviews for paid orders
    ).exists()

    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect(product.get_absolute_url())
    
    # 2. Check if the user has already reviewed this product
    if ProductReview.objects.filter(customer=request.user, product=product).exists():
        messages.info(request, "You have already submitted a review for this product.")
        return redirect(product.get_absolute_url())

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.verified_purchase = True # Set verified purchase flag
            review.save()
            messages.success(request, "Thank you! Your review has been submitted.")
            return redirect(product.get_absolute_url())
    else:
        form = ProductReviewForm()

    context = {
        'form': form,
        'product': product
    }
    return render(request, 'reviews/add_review.html', context)
