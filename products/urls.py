from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # URL for sellers to request a new product be added to the catalog
    path('request-new/', views.request_new_product_view, name='request_new_product'),
    
    # API endpoint to fetch data for a specific product variant
    path('api/variant/<int:variant_id>/', views.get_variant_data_api, name='get_variant_data_api'),
    
    # The main product detail page, must be last as it's a general catch-all
    path('<str:parent_asin>/', views.product_detail, name='product_detail'),
]
