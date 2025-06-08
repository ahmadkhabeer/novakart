from django.contrib import admin
from .models Category, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'stock', 'available', 'created_at', 'updated_at')
    list_filter = ('available', 'created_at', 'updated_at', 'category')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'available')
    prepopulated_fields = {'slug': ('name',)}
    raw_id_fields = ('category',)
    