from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Checkout and Order Placement
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),
    
    # Order History and Detail
    path('history/', views.order_history_view, name='order_history'),
    path('history/<int:order_id>/', views.order_detail_view, name='order_detail'),
    
    # Customer Returns
    path('history/<int:order_id>/return/', views.initiate_return_view, name='initiate_return'),
]
