from django.contrib import admin
from .models import Seller, Offer

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'rating')
    search_fields = ('name', 'user__username')
    list_select_related = ('user',)
    raw_id_fields = ('user',) # Good for lots of users

@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'price', 'quantity', 'seller', 'is_buybox_winner', 'is_active')
    list_filter = ('is_active', 'is_buybox_winner', 'fulfillment_type', 'condition', 'seller')
    search_fields = ('variant__child_asin', 'variant__parent_product__title', 'seller__name')
    list_editable = ('price', 'quantity', 'is_buybox_winner', 'is_active')
    autocomplete_fields = ('variant', 'seller')
    list_select_related = ('variant', 'seller')
