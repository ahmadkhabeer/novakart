from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # URL for sellers to request a new product be added to the catalog
    path('request-new/', views.request_new_product_view, name='request_new_product'),
    
    # The API endpoint URL has been removed as it is no longer used.
    
    # The main product detail page, which matches any string for the ASIN.
    # It's good practice to keep this as the last pattern.
    path('<str:parent_asin>/', views.product_detail, name='product_detail'),
]
