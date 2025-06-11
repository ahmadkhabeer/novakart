from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, Shipment, ReturnRequest, ReturnItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    list_display = ['offer', 'price_at_purchase', 'quantity']
    readonly_fields = ('offer', 'price_at_purchase', 'quantity')
    extra = 0
    can_delete = False

class ReturnRequestInline(admin.TabularInline):
    model = ReturnRequest
    fields = ('requested_at', 'status', 'reason')
    readonly_fields = ('requested_at', 'status', 'reason')
    extra = 0
    can_delete = False
    def has_add_permission(self, request, obj=None):
        return False

class ShipmentInline(admin.TabularInline):
    model = Shipment
    autocomplete_fields = ('items',) # This line now works because of the new OrderItemAdmin below
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'paid', 'created_at', 'total_paid')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('id', 'user__username', 'shipping_address__full_name')
    readonly_fields = ('user', 'shipping_address', 'created_at', 'updated_at', 'paid', 'total_paid')
    inlines = [OrderItemInline, ShipmentInline, ReturnRequestInline]

    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return False

# --- NEW: REGISTER THE OrderItem MODEL ---
# This is the fix. By registering OrderItem with its own admin class
# and defining search_fields, we allow other parts of the admin
# (like ShipmentInline) to reference it for autocomplete functionality.
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'offer', 'quantity', 'price_at_purchase')
    list_select_related = ('order', 'offer__seller', 'offer__variant__parent_product')
    search_fields = [
        'offer__variant__parent_product__title', # Search by product title
        'offer__seller__name',                   # Search by seller name
        'order__id',                             # Search by order ID
    ]
# --- END FIX ---


@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('order__id', 'user__username')
    autocomplete_fields = ('order', 'user')

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'country')
    search_fields = ('full_name', 'user__username', 'city', 'postal_code')
