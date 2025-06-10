from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extends the default User model to store additional information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class ShippingAddress(models.Model):
    """
    Stores a shipping address, owned by a specific user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=255)
    address_line_1 = models.CharField("Address Line 1", max_length=255)
    address_line_2 = models.CharField("Address Line 2", max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state_province_region = models.CharField("State/Province/Region", max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False, help_text="Is this the default shipping address?")

    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
        ordering = ['-is_default']

    def __str__(self):
        return f"{self.user.username} - {self.address_line_1}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            self.user.addresses.all().update(is_default=False)
        super().save(*args, **kwargs)

class PaymentMethod(models.Model):
    class CardType(models.TextChoices):
        VISA = 'VISA', 'Visa'
        MASTERCARD = 'MC', 'Mastercard'
        AMEX = 'AMEX', 'American Express'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payment_methods')
    card_type = models.CharField(max_length=4, choices=CardType.choices)
    cardholder_name = models.CharField(max_length=255)
    last_four_digits = models.CharField(max_length=4)
    expiry_month = models.PositiveSmallIntegerField()
    expiry_year = models.PositiveSmallIntegerField()
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_card_type_display()} ending in {self.last_four_digits}"

class WishList(models.Model):
    """
    A persistent, named list of products for a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlists')
    name = models.CharField(max_length=100, default='My Wish List')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

class WishListItem(models.Model):
    """
    An individual product within a user's Wish List.
    """
    wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='wishlist_items')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('wishlist', 'product')

    def __str__(self):
        return f"{self.product.title} in {self.wishlist.name}"

class BrowseHistory(models.Model):
    """
    Tracks products recently viewed by a user.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Browse_history')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Browse History'
