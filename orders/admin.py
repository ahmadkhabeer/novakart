from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress

class OrderItemInline(admin.TabularInline):
    """
    Allows viewing and editing of OrderItems directly within the Order admin page.
    """
    model = OrderItem
    # Fields to display for each inline item
    list_display = ['offer', 'price_at_purchase', 'quantity']
    # Fields that should not be editable by the admin once created
    readonly_fields = ('offer', 'price_at_purchase', 'quantity')
    # Disallow adding new items to a completed order via the admin
    extra = 0
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'paid', 'created_at', 'total_paid')
    list_filter = ('status', 'paid', 'created_at')
    search_fields = ('id', 'user__username', 'shipping_address__full_name')
    
    # Define fields that should not be changed by an admin to preserve order integrity.
    readonly_fields = (
        'user', 
        'shipping_address', 
        'created_at', 
        'updated_at',
        'paid',
        'total_paid'
    )
    
    # Include the OrderItem records directly on this page for easy viewing.
    inlines = [OrderItemInline]

    # Prevent admins from creating new orders manually (should come from the storefront).
    def has_add_permission(self, request):
        return False

    # Prevent admins from deleting orders (should be cancelled instead).
    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'country')
    search_fields = ('full_name', 'user__username', 'city', 'postal_code')
