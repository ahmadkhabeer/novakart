from django.db import models
from django.conf import settings
from decimal import Decimal

# CORRECTED: Import the models from their final locations.
from marketplace.models import Offer
from users.models import ShippingAddress

class Order(models.Model):
    """
    Represents a completed customer order.
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    
    # CRITICAL CHANGE: This now links to the address record in the 'users' app.
    # The on_delete=models.PROTECT rule prevents an address from being deleted
    # if it's tied to a past order, preserving order history.
    shipping_address = models.ForeignKey(ShippingAddress, related_name='orders', on_delete=models.PROTECT, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f'Order {self.id} by {self.user.username if self.user else "Guest"}'


class OrderItem(models.Model):
    """
    Represents a single item within an Order.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    
    # This relationship is correct. It freezes the offer at the time of purchase.
    offer = models.ForeignKey(Offer, related_name='order_items', on_delete=models.PROTECT)
    
    # This is also correct. It freezes the price, so future price changes on the 
    # offer do not affect the historical order record.
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price_at_purchase * self.quantity
