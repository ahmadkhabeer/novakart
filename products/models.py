from django.db import models
from django.urls import reverse

class BrowseNode(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        verbose_name_plural = 'Browse Nodes'

    def __str__(self):
        return self.name

class Product(models.Model):
    parent_asin = models.CharField(max_length=10, unique=True, help_text="ASIN for the parent product.")
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    browse_nodes = models.ManyToManyField(BrowseNode, related_name='products')
    is_variation_parent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'parent_asin': self.parent_asin})

    def __str__(self):
        return self.title

class ProductVariant(models.Model):
    child_asin = models.CharField(max_length=10, unique=True, help_text="ASIN for the specific variant.")
    parent_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.parent_product.title} ({self.child_asin})"

class Attribute(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class VariantAttribute(models.Model):
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='attributes')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('variant', 'attribute_value')

    def __str__(self):
        return f"{self.variant} -> {self.attribute_value}"
