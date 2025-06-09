from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Main account dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Auth
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(next_page='core:product_list'), name='logout'),

    # Profile Settings
    path('profile/', views.profile_settings, name='profile_settings'),

    # Shipping Address CRUD
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/edit/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),
]
