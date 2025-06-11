from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('become-a-seller/', views.seller_register_view, name='seller_register'),
]
