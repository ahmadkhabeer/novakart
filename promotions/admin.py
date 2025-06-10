from django.contrib import admin
from .models import Promotion, Deal

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('name', 'promo_code', 'discount_type', 'value', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active', 'discount_type', 'start_date', 'end_date')
    search_fields = ('name', 'promo_code')
    list_editable = ('is_active',)

@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('offer', 'deal_price', 'start_time', 'end_time', 'is_active')
    list_filter = ('is_active', 'start_time', 'end_time')
    search_fields = ('offer__variant__parent_product__title', 'offer__seller__name')
    list_editable = ('is_active', 'deal_price')
    autocomplete_fields = ('offer',)
    list_select_related = ('offer__variant__parent_product', 'offer__seller')
