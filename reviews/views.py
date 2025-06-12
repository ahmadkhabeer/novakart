from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProductReview, ProductQuestion, ProductAnswer
from products.models import Product
from orders.models import OrderItem
from .forms import ProductReviewForm, QuestionForm, AnswerForm

# --- Product Review View ---

@login_required
def add_review(request, product_id):
    """
    Processes the submission of a product review, ensuring the user has purchased the item.
    """
    product = get_object_or_404(Product, id=product_id)

    # 1. Check if the user has purchased this product in a paid order.
    has_purchased = OrderItem.objects.filter(
        order__user=request.user,
        offer__variant__parent_product=product,
        order__paid=True
    ).exists()

    if not has_purchased:
        messages.error(request, "You can only review products you have purchased.")
        return redirect(product.get_absolute_url())
    
    # 2. Check if the user has already reviewed this product.
    if ProductReview.objects.filter(customer=request.user, product=product).exists():
        messages.info(request, "You have already submitted a review for this product.")
        return redirect(product.get_absolute_url())

    if request.method == 'POST':
        form = ProductReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.product = product
            review.verified_purchase = True
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


# --- Question & Answer Views ---

@login_required
def ask_question_view(request, product_id):
    """
    Processes the submission of a customer question for a specific product.
    """
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.customer = request.user
            question.product = product
            question.save()
            messages.success(request, "Your question has been posted.")
    # Always redirect back to the product page, whether the request was GET or POST.
    return redirect(product.get_absolute_url())

@login_required
def post_answer_view(request, question_id):
    """
    Processes the submission of an answer for a specific question.
    """
    question = get_object_or_404(ProductQuestion, id=question_id)
    if request.method == 'POST':
        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(commit=False)
            answer.customer = request.user
            answer.question = question
            answer.save()
            messages.success(request, "Thank you for your answer.")
    # Always redirect back to the product page where the question was.
    return redirect(question.product.get_absolute_url())
