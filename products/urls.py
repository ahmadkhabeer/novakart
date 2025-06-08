from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('<str:parent_asin>/', views.product_detail, name='product_detail'),
]
