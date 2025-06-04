from django.db import models
from django.urls import reverse

class Category(models.Model):
    """
    Represents a product category in the e-commerce store.
    Each category has a unique name and a URL-friendly slug.
    """
    name = models.CharField(max_length=255, db_index=True, unique=True,
                            help_text='The name of the product category (e.g., "Electronics", "Books").')
    slug = models.SlugField(max_length=255, unique=True,
                            help_text='A URL-friendly unique identifier for the category (e.g., "electronics").')
    description = models.TextField(blank=True, null=True,
                                   help_text='A brief description of the category.')
    created_at = models.DateTimeField(auto_now_add=True,
                                      help_text='Timestamp when the category was created.')

    updated_at = models.DateTimeField(auto_now=True,
                                      help_text='Timestamp when the category was last updated.')

    class Meta():
        """
        Meta options for the Category model.
        """
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'
    
    def get_absolute_url(self):
        """
        Returns the URL to a specific category's product list.
        This is a placeholder and assumes a URL pattern named 'shop:product_list_by_category'.
        """
        return reverse('products:product_list_by_category', args=[self.slug])
  
    def __str__(self):
        """
        String representation of the Category object.
        """
        return self.name

class Product(models.Model):
    """
    Represents a product available for sale in the e-commerce store.
    Includes details like category, name, price, stock, and availability.
    """
    category = models.ForeignKey(Category, 
                                 related_name='products',
                                 on_delete=models.CASCADE,
                                 help_text='The category the product belongs to.')
    
    name = models.CharField(max_length=255, db_index=True, unique=True,
                            help_text='The name of the product.')
    slug = models.SlugField(max_length=255, db_index=True, unique=True,
                            help_text='A URL-friendly unique identifier for the product.')
    description = models.TextField(blank=True, null=True,
                            help_text='A detailed description of the product.')
    price = models.DecimalField(max_digits=10, decimal_places=2,
                            help_text='The selling price of the product (e.g., 99.99).')
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True, null=True,
                            help_text="Path to the product's image file.")
    stock = models.PositiveIntegerField(help_text='Current quantity of the product in stock.')
    available = models.BooleanField(default=True,
                            help_text='Indicates if the product is currently available for purchase.')
    created_at = models.DateTimeField(auto_now_add=True,
                            help_text='Timestamp when the product was added.')
    updated_at = models.DateTimeField(auto_now=True,
                            help_text='Timestamp when the product was last updated.')

    class Meta():
        """
        Meta options for the Product model.
        """
        ordering = ('name',)
        verbose_name = 'product'
        verbose_name_plural = 'products'
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['-created_at'])
        ]
        
    def get_absolute_url(self):
        """
        Returns the URL to a specific product's detail page.
        This is a placeholder and assumes a URL pattern named 'shop:product_detail'.
        """
        return reverse('products:product_detail', args = [self.id, self.slug])
    
    def __str__(self):
        """
        String representation of the Product object.
        """
        return self.name
