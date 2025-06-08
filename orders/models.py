from django.db import models
from django.conf import settings
from marketplace.models import Offer
from decimal import Decimal

# NEW: A model to store a snapshot of the shipping address for an order.
class ShippingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField("Address Line 1", max_length=255)
    address_line_2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province_region = models.CharField("State/Province/Region", max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"

    def __str__(self):
        return f"{self.full_name}, {self.address_line_1}, {self.city}"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # MODIFIED: Link to a frozen address record instead of storing fields directly.
    shipping_address = models.ForeignKey(ShippingAddress, related_name='orders', on_delete=models.PROTECT)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f'Order {self.id} by {self.user.username if self.user else "Guest"}'

    # The calculation can still be a method, but the final value should be stored.
    def calculate_total(self):
        # Recalculates total based on its items.
        total = sum(item.get_cost() for item in self.items.all())
        self.total_paid = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    offer = models.ForeignKey(Offer, related_name='order_items', on_delete=models.PROTECT)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price_at_purchase * self.quantity
