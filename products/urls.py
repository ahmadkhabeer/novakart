from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    # The outdated path for the api/variant/ view has been removed from this list.
    
    # The main product detail page, which matches any string for the ASIN.
    path('<str:parent_asin>/', views.product_detail, name='product_detail'),
]
