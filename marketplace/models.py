from django.db import models
from django.conf import settings
from products.models import ProductVariant

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.name

class Offer(models.Model):
    FULFILLMENT_CHOICES = [('FBA', 'Fulfilled by NovaKart'), ('FBM', 'Fulfilled by Merchant')]
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='offers')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='offers')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    condition = models.CharField(max_length=50, default='New')
    fulfillment_type = models.CharField(max_length=3, choices=FULFILLMENT_CHOICES)
    is_buybox_winner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.variant} by {self.seller} for ${self.price}"
