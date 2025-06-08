from django.db import models
from django.contrib.auth import get_user_model
from marketplace.models import Offer

User = get_user_model()

class Order(models.Model):
    """
    Stores details about each customer order.
    Includes customer information, shipping address, total amount, and order status.
    It links to the user who placed the order (if not a guest).
    """
    user = models.ForeignKey(User, related_name='orders', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=100,
                                  help_text="First name of the person placing the order.")
    last_name = models.CharField(max_length=100,
                                 help_text="Last name of the person placing the order.")
    email = models.EmailField(max_length=255,
                              help_text="Email of the person placing the order.")
    address_line_1 = models.CharField(max_length=255, 
                                      help_text="Shipping address line 1.")
    address_line_2 = models.CharField(max_length=255,
                                      help_text="Shipping address line 2.")
    city = models.CharField(max_length=100,
                            help_text="Shipping city.")
    state = models.CharField(max_length=100, blank=True, null=True,
                             help_text="Shipping state.")
    postal_code = models.CharField(max_length=20,
                                   help_text="Shipping postal code.")
    country = models.CharField(max_length=100,
                               help_text="Shipping country.")
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="Phone number for the order contact.")
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text="Timestamp when the order was created.")
    updated_at = models.DateTimeField(auto_now=True,
                                      help_text="Timestamp when the order was last updated.")
    paid = models.BooleanField(default=False,
                               help_text="Indicates if the order has been paid for.")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                       help_text="The total cost of the order.")
    
    ORDER_STATUS_CHOICES = [
        ('Pending','Pending'),
        ('Processing','Processing'),
        ('Shipped','Shipped'),
        ('Delivered','Delivered'),
        ('Cancelled','Cancelled'),
        ('Refunded','Refunded'),
    ]
    
    status = models.CharField(max_length=100, choices=ORDER_STATUS_CHOICES, default='Pending',
                              help_text="Current status of the order (e.g., 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled').")
    class Meta:
        """
        Meta options for the Order model.
        """
        ordering = ('-created_at',)
    
    def get_total_cost(self):
        """
        Calculates the total cost of the order by summing up all order items.
        """
        return sum(item.get_cost() for item in self.items.all())

    def __str__(self):
        """
        String representation of the Order object.
        """
        return f'Order {self.id} by {self.first_name} {self.last_name}'

class OrderItem(models.Model):
    """
    Stores the individual products included in each order,
    linking an order to specific products and recording the price and quantity
    at the time of purchase.
    """
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey('products.Product', related_name='order_items',
                                on_delete=models.CASCADE,
                                help_text="The product included in this order item.")
    offer = models.ForeignKey(Offer, related_name='order_items', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        """
        Meta options for the OrderItem model.
        """
        unique_together = ('order', 'product')
        ordering = ('id',)
        
    def get_cost(self):
        """
        Calculates the cost of this individual order item.
        """
        return self.price * self.quantity

    def __str__(self):
        """
        String representation of the OrderItem object.
        """
        return f'Item {self.id} for order {self.order.id}: {self.product.name} x {self.quantity}'
