from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class BrowseNode(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Attribute(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=255)

    class Meta:
        unique_together = ('attribute', 'value')
        ordering = ['attribute__name', 'value']

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

class Product(models.Model):
    parent_asin = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(blank=True)
    browse_nodes = models.ManyToManyField(BrowseNode, related_name='products', blank=True)
    is_variation_parent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'parent_asin': self.parent_asin})

    def get_feature_image(self):
        return self.images.filter(is_feature=True).first()

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=255, blank=True)
    is_feature = models.BooleanField(default=False, help_text="Is this the main image for the parent product?")

    def __str__(self):
        return self.alt_text or f"Image for {self.product.title}"

    def save(self, *args, **kwargs):
        if self.is_feature:
            self.product.images.filter(is_feature=True).update(is_feature=False)
        super().save(*args, **kwargs)

class ProductVariant(models.Model):
    parent_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    child_asin = models.CharField(max_length=255, unique=True)
    attributes = models.ManyToManyField(AttributeValue, related_name='variants')
    images = models.ManyToManyField('ProductImage', related_name='variants', blank=True)

    def __str__(self):
        attr_values = ", ".join(str(attr) for attr in self.attributes.all().order_by('attribute__name'))
        return f"{self.parent_product.title} ({attr_values or self.child_asin})"

    def get_best_offer(self):
        return self.offers.filter(is_active=True).order_by('price').first()


# --- NEW MODEL FOR SELLER PRODUCT REQUESTS ---

class ProductRequest(models.Model):
    """
    A model for sellers to request the addition of a new product to the catalog.
    """
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    # Use a string reference to avoid circular imports
    seller = models.ForeignKey('marketplace.Seller', on_delete=models.CASCADE, related_name='product_requests')
    title = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    admin_notes = models.TextField(blank=True, null=True, help_text="Notes for the seller, e.g., why a request was rejected.")

    def __str__(self):
        return f"Request for '{self.title}' by {self.seller.name} ({self.status})"

    class Meta:
        ordering = ['-created_at']
