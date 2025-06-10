from django.db import models
from django.utils import timezone

class Promotion(models.Model):
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENT', 'Percentage'
        FIXED_AMOUNT = 'FIXED', 'Fixed Amount'

    name = models.CharField(max_length=255)
    promo_code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DiscountType.choices)
    value = models.DecimalField(max_digits=10, decimal_places=2, help_text="The percentage or fixed amount of the discount.")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date

    def __str__(self):
        return self.name

class Deal(models.Model):
    offer = models.ForeignKey('marketplace.Offer', on_delete=models.CASCADE, related_name='deals')
    deal_price = models.DecimalField(max_digits=10, decimal_places=2)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def is_valid(self):
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time
    
    def __str__(self):
        return f"Deal on {self.offer} for ${self.deal_price}"
