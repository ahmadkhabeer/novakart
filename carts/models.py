from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Cart(models.Model):
    """
    Represents a persistent shopping cart for a user.
    Each user can have one dedicated cart.
    """
    user = models.OneToOneField(User, related_name='cart',
                                on_delete=models.CASCADE, primary_key=True,
                                help_text="The user who owns this cart. (One user, one cart).")
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text="Timestamp when the cart was created.")
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text="Timestamp when the cart was last updated.")
    
    def get_total_price(self):
        """
        Calculates the total price of all items in the cart.
        """
        return sum(item.get_price() for item in self.items.all())

    def __str__(self):
        """
        String representation of the Cart object.
        """
        return f'Cart for {self.user.username}'

class CartItem(models.Model):
    """
    Stores items within a persistent cart, linking products and quantities
    to a specific cart. Ensures a product appears only once per cart.
    """
    cart = models.ForeignKey(Cart, related_name='items',
                             on_delete=models.CASCADE,
                             help_text="The cart this item belongs to.")
    product = models.ForeignKey('products.Product', related_name='cart_items',
                                on_delete=models.CASCADE,
                                help_text="The product in this cart item.")
    quantity = models.PositiveIntegerField(default=1,
                                           help_text="The quantity of the product in the cart.")
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text="Timestamp when the cart item was added.")
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text="Timestamp when the cart item was last updated.")
    
    class Meta:
        """
        Meta options for the CartItem model.
        """
        unique_together = ('cart', 'product')
        ordering = ('id',)    

    def get_price(self):
        """
        Calculates the total price for this cart item (product price * quantity).
        """
        return self.product.price * self.quantity

    def __str__(self):
        """
        String representation of the CartItem object.
        """
        return f'{self.quantity} x {self.product.name} in cart {self.cart.user.username}'
