from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at', 'display_total_price')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    
    def display_total_price(self, obj):
        return obj.get_total_price()
    
    display_total_price.short_description = 'Total price'

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'display_item_price', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at', 'product__category')
    search_fields = ('cart__user__username', 'product__name')
    raw_id_fields = ('cart', 'product')
    list_editable = ('quantity',)
    readonly_fields = ('created_at', 'updated_at')
    
    def display_item_price(self, obj):
        return obj.get_price()
    
    display_item_price.short_description = 'Item Total Price'