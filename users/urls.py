from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(next_page='core:product_list'), name='logout'),
    path('profile/', views.profile_settings, name='profile_settings'),

    # Address CRUD
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/edit/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),

    # NEW PAYMENT METHOD URLS
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
    path('payment-methods/<int:pk>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('payment-methods/<int:pk>/set-default/', views.payment_method_set_default, name='payment_method_set_default'),
]
