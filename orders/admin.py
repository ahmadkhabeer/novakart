from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress, Shipment, ReturnRequest, ReturnItem

# Define an inline for Return Requests to show on the Order page
class ReturnRequestInline(admin.TabularInline):
    model = ReturnRequest
    fields = ('requested_at', 'status', 'reason')
    readonly_fields = ('requested_at', 'status', 'reason')
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

# You can also create an inline for shipments
class ShipmentInline(admin.TabularInline):
    model = Shipment
    autocomplete_fields = ('items',)
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'paid', 'created_at', 'total_paid')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('id', 'user__username', 'shipping_address__full_name')
    readonly_fields = ('user', 'shipping_address', 'created_at', 'updated_at', 'paid', 'total_paid')
    
    # Add the new inlines here
    inlines = [ShipmentInline, ReturnRequestInline] # ShipmentInline was also a good addition

# You should also register the new models so they can be managed independently
@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'user', 'status', 'requested_at')
    list_filter = ('status', 'requested_at')
    search_fields = ('order__id', 'user__username')
    autocomplete_fields = ('order', 'user')

# The other admin classes from before should still be here
@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'country')
    search_fields = ('full_name', 'user__username', 'city', 'postal_code')
