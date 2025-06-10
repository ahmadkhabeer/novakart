from django.contrib import admin
from .models import Profile, ShippingAddress, PaymentMethod, WishList, WishListItem, BrowseHistory

# This inline will let you see wishlist items directly inside the WishList admin page
class WishListItemInline(admin.TabularInline):
    model = WishListItem
    autocomplete_fields = ('product',)
    extra = 0

@admin.register(WishList)
class WishListAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'created_at')
    search_fields = ('user__username', 'name')
    inlines = [WishListItemInline]

@admin.register(BrowseHistory)
class BrowseHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'timestamp')
    list_filter = ('timestamp',)
    search_fields = ('user__username', 'product__title')
    autocomplete_fields = ('user', 'product')
    readonly_fields = ('user', 'product', 'timestamp') # History should not be editable

# You should also register your other new models
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_type', 'cardholder_name', 'last_four_digits', 'is_default')
    list_filter = ('card_type', 'is_default')
    search_fields = ('user__username', 'cardholder_name')
