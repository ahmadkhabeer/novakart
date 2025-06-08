from django.contrib import admin
from .models import BrowseNode, Product, ProductVariant, Attribute, AttributeValue, VariantAttribute

@admin.register(BrowseNode)
class BrowseNodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('parent',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'parent_asin', 'brand', 'is_variation_parent', 'created_at')
    search_fields = ('title', 'parent_asin', 'brand', 'description')
    list_filter = ('is_variation_parent', 'brand', 'created_at')
    filter_horizontal = ('browse_nodes',) # Better for ManyToMany fields

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('child_asin', 'parent_product', 'created_at')
    search_fields = ('child_asin', 'parent_product__title')
    list_select_related = ('parent_product',) # Optimizes query
    autocomplete_fields = ('parent_product',)

@admin.register(Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'attribute')
    search_fields = ('value', 'attribute__name')
    list_filter = ('attribute',)
    autocomplete_fields = ('attribute',)

@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ('variant', 'attribute_value')
    autocomplete_fields = ('variant', 'attribute_value')
