from django.contrib import admin
from .models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    """
    Displays CartItem records directly within the Cart admin page.
    This provides a clear, at-a-glance view of what's inside each cart.
    """
    model = CartItem
    
    # Fields to display for each inline item.
    list_display = ('offer', 'quantity', 'is_saved_for_later', 'added_at')
    
    # These fields should not be editable by an admin in this view
    # to maintain data integrity. They are set by user actions.
    readonly_fields = ('offer', 'quantity', 'added_at')
    
    # Autocomplete fields make it easier to select related objects if needed.
    autocomplete_fields = ('offer',)
    
    # Controls how many extra blank forms are shown. 0 is clean.
    extra = 0


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Cart model.
    """
    # Use the inline class to show cart items on this page.
    inlines = [CartItemInline]
    
    # The primary fields to display in the main cart list view.
    # Now includes session_key for guest identification.
    list_display = ('id', 'user', 'session_key', 'created_at', 'updated_at')
    
    # Filters to help staff find carts easily.
    list_filter = ('created_at', 'updated_at')
    
    # Search functionality for finding specific carts.
    search_fields = ('user__username', 'session_key')
    
    # Fields that should be read-only on the detail page.
    # A cart's user or session is fundamental and shouldn't be changed lightly.
    readonly_fields = ('user', 'session_key', 'created_at', 'updated_at')

    class Meta:
        model = Cart
