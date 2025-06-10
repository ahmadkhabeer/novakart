from django.urls import path
from . import views

app_name = 'promotions'

urlpatterns = [
    path('deals/', views.deal_list_view, name='deal_list'),
]
