from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('become-a-seller/', views.seller_register_view, name='seller_register'),
    path('dashboard/', views.seller_dashboard_view, name='seller_dashboard'),

    # NEW URLS FOR CREATING OFFERS
    # The first step is selecting a product
    path('offers/add/', views.offer_create_product_select_view, name='offer_add'),
    # The second step takes the ID of the chosen variant
    path('offers/add/<int:variant_id>/', views.offer_create_view, name='offer_create'),
]
