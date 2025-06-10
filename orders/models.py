from django.db import models
from django.conf import settings
from decimal import Decimal

from marketplace.models import Offer
from users.models import ShippingAddress
from promotions.models import Promotion

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        SHIPPED = 'SHIPPED', 'Shipped'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    shipping_address = models.ForeignKey(ShippingAddress, related_name='orders', on_delete=models.PROTECT, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    paid = models.BooleanField(default=False)
    
    # Gifting and Promotions
    is_gift = models.BooleanField(default=False)
    gift_message = models.TextField(blank=True, null=True)
    promotions_applied = models.ManyToManyField(Promotion, blank=True, related_name='orders')

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Order"
        verbose_name_plural = "Orders"

    def __str__(self):
        return f'Order {self.id} by {self.user.username if self.user else "Guest"}'

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

class Shipment(models.Model):
    class ShipmentStatus(models.TextChoices):
        PREPARING = 'PREPARING', 'Preparing for Shipment'
        SHIPPED = 'SHIPPED', 'Shipped'
        IN_TRANSIT = 'IN_TRANSIT', 'In Transit'
        DELIVERED = 'DELIVERED', 'Delivered'

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipments')
    items = models.ManyToManyField(OrderItem, related_name='shipments')
    seller = models.ForeignKey('marketplace.Seller', on_delete=models.PROTECT, related_name='shipments')
    status = models.CharField(max_length=20, choices=ShipmentStatus.choices, default=ShipmentStatus.PREPARING)
    tracking_number = models.CharField(max_length=100, blank=True, null=True)
    carrier = models.CharField(max_length=50, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    shipped_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Shipment for Order #{self.order.id} from {self.seller.name}"

class ReturnRequest(models.Model):
    class ReturnStatus(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        AUTHORIZED = 'AUTHORIZED', 'Authorized'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        REJECTED = 'REJECTED', 'Rejected'

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name='return_requests')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=ReturnStatus.choices, default=ReturnStatus.REQUESTED)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Return Request for Order #{self.order.id}"

class ReturnItem(models.Model):
    return_request = models.ForeignKey(ReturnRequest, on_delete=models.CASCADE, related_name='items')
    order_item = models.ForeignKey(OrderItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} of {self.order_item} for Return Request #{self.return_request.id}"
