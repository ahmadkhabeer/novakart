from django.db import models
from django.conf import settings
from marketplace.models import Offer

class Cart(models.Model):
    """
    A model that represents a user's or guest's shopping cart.
    It can be associated with a logged-in user or an anonymous session.
    """
    # CORRECTED: A cart doesn't always have a user (guests).
    # So we use a nullable ForeignKey instead of a OneToOneField.
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    
    # NEW: To track carts for users who are not logged in.
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.user:
            return f"User Cart for {self.user.username}"
        return f"Guest Cart (Session: {self.session_key})"

class CartItem(models.Model):
    """
    Represents an item within a cart, linking to a specific seller's offer.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    # NEW: To allow for "Save for Later" functionality within the cart.
    is_saved_for_later = models.BooleanField(default=False)
    
    # NEW: To track when an item was added.
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        # An offer can only appear once per cart (either active or saved for later)
        unique_together = ('cart', 'offer')

    def __str__(self):
        return f"{self.quantity} x {self.offer.variant.parent_product.title} in cart {self.cart.id}"

    def get_total_price(self):
        # The price is always live from the offer.
        return self.offer.price * self.quantity
