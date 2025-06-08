from django.contrib import admin
from .models import ProductReview, ProductQuestion, ProductAnswer

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'product', 'customer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at', 'product')
    search_fields = ('title', 'text', 'product__title', 'customer__username')
    autocomplete_fields = ('product', 'customer')
    list_select_related = ('product', 'customer')

@admin.register(ProductQuestion)
class ProductQuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'product', 'customer', 'created_at')
    list_filter = ('created_at', 'product')
    search_fields = ('text', 'product__title', 'customer__username')
    autocomplete_fields = ('product', 'customer')
    list_select_related = ('product', 'customer')

@admin.register(ProductAnswer)
class ProductAnswerAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'customer', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'question__text', 'customer__username')
    autocomplete_fields = ('question', 'customer')
    list_select_related = ('question', 'customer')
