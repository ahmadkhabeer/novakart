from django.db import models
from django.conf import settings
from marketplace.models import Offer
from promotions.models import Promotion
from decimal import Decimal

class Cart(models.Model):
    """
    A model that represents a user's or guest's shopping cart.
    It can be associated with a logged-in user or an anonymous session.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # --- NEW REUSABLE METHOD ---
    def get_totals(self, promo_id=None):
        """
        Calculates subtotal, discount, and final total for the cart.
        This centralizes the pricing logic for use in multiple views.
        """
        subtotal = sum(item.get_total_price() for item in self.items.filter(is_saved_for_later=False))
        discount = Decimal('0.00')
        
        if promo_id:
            try:
                promo = Promotion.objects.get(id=promo_id)
                if promo.is_valid():
                    if promo.discount_type == Promotion.DiscountType.PERCENTAGE:
                        discount = (subtotal * (promo.value / 100)).quantize(Decimal('0.01'))
                    else: # Fixed amount
                        discount = promo.value
            except Promotion.DoesNotExist:
                pass
        
        final_total = subtotal - discount
        return {'subtotal': subtotal, 'discount': discount, 'final_total': final_total}

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
    is_saved_for_later = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['added_at']
        unique_together = ('cart', 'offer')

    def __str__(self):
        return f"{self.quantity} x {self.offer.variant.parent_product.title} in cart {self.cart.id}"

    def get_total_price(self):
        return self.offer.price * self.quantity
