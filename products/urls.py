from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # The outdated path for 'request-new/' has been removed from this list.
    
    # API endpoint to fetch data for a specific product variant
    path('api/variant/<int:variant_id>/', views.get_variant_data_api, name='get_variant_data_api'),
    
    # The main product detail page
    path('<str:parent_asin>/', views.product_detail, name='product_detail'),
]
