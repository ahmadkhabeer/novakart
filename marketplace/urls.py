from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('become-a-seller/', views.seller_register_view, name='seller_register'),
    path('dashboard/', views.seller_dashboard_view, name='seller_dashboard'),

    # Offer creation flow
    path('offers/add/', views.offer_create_product_select_view, name='offer_add'),
    path('offers/add/<int:variant_id>/', views.offer_create_view, name='offer_create'),

    # NEW: Offer management URLs
    path('offers/<int:offer_id>/edit/', views.offer_update_view, name='offer_edit'),
    path('offers/<int:offer_id>/delete/', views.offer_delete_view, name='offer_delete'),
]
