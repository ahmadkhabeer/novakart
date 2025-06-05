from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)
    extra = 1
    readonly_fields = ('price', 'get_cost')

    def get_cost(self, obj):
        return obj.get_cost()
    
    get_cost.short_description = 'Item Cost'

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_email', 'first_name', 'last_name', 'paid', 'status', 'total_amount', 'created_at')
    list_filter = ('paid', 'status', 'created_at', 'updated_at')
    search_fields = ('id', 'user__username', 'user__email', 'first_name', 'last_name', 'email')
    list_editable = ('paid', 'status')
    raw_id_fields = ('user',)
    inlines = [OrderItemInline]
    readonly_fields = ('created_at', 'updated_at', 'total_amount_display')
    
    def user_email(self, obj):
        if obj.user:
            return obj.user.email
        return obj.email
    
    user_email.short_description = 'User/Order Email'
    
    def total_amount_display(self, obj):
        return obj.total_amount
    
    total_amount_display.short_description = 'Total Amount'
    