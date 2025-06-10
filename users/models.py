from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """
    Extends the default User model to store additional information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # Example future fields:
    # phone_number = models.CharField(max_length=20, blank=True)
    # profile_picture = models.ImageField(upload_to='users/pictures', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create a Profile automatically when a new User is created.
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
        # Ensure only one address can be the default
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
    # In a real app, this would link to a token from a payment provider like Stripe or Braintree
    # provider_token = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return f"{self.get_card_type_display()} ending in {self.last_four_digits}"
