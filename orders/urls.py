from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('place-order/', views.place_order_view, name='place_order'),
    path('success/<int:order_id>/', views.order_success_view, name='order_success')
]
