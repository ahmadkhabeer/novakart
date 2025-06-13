from django.contrib import admin
from django.utils.html import format_html

# Import all models, including the new ProductRequest
from .models import (
    BrowseNode, Attribute, AttributeValue, 
    Product, ProductVariant, ProductImage, ProductRequest
)

@admin.register(BrowseNode)
class BrowseNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute')
    list_filter = ('attribute',)
    search_fields = ('value',)
    autocomplete_fields = ('attribute',)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ('attributes', 'images',)
    autocomplete_fields = ('attributes',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'parent_asin', 'is_variation_parent')
    search_fields = ('title', 'brand', 'parent_asin')
    list_filter = ('browse_nodes', 'brand', 'is_variation_parent')
    filter_horizontal = ('browse_nodes',)
    inlines = [ProductImageInline, ProductVariantInline]

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'child_asin', 'parent_product')
    search_fields = ('child_asin', 'parent_product__title', 'attributes__value')
    list_filter = ('parent_product',)
    filter_horizontal = ('attributes', 'images',)
    autocomplete_fields = ('attributes', 'parent_product',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'product', 'is_feature', 'image_preview')
    list_filter = ('product', 'is_feature')
    search_fields = ('alt_text', 'product__title')
    autocomplete_fields = ('product',)

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.image.url)
        return "No Image"
    image_preview.short_description = 'Preview'


# --- NEW: ADMIN FOR MANAGING SELLER PRODUCT REQUESTS ---
@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    """
    Admin interface for reviewing and managing product requests from sellers.
    """
    list_display = ('title', 'seller', 'brand', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'brand', 'seller__name')
    
    # Allows admins to change the status directly from the list view
    list_editable = ('status',)
    
    # When viewing a single request, these fields cannot be edited by the admin
    readonly_fields = ('seller', 'title', 'brand', 'description', 'created_at')
    
    # For a better UI when selecting a seller
    autocomplete_fields = ('seller',)

    # Define fieldsets for a cleaner layout in the detail view
    fieldsets = (
        ('Request Details', {
            'fields': ('title', 'brand', 'seller', 'description', 'created_at')
        }),
        ('Admin Review', {
            'fields': ('status', 'admin_notes')
        }),
    )
