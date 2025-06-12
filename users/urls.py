from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Auth & Account Management
    path('dashboard/', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.UserLoginView.as_view(), name='login'),
    path('logout/', views.UserLogoutView.as_view(), name='logout'),
    path('profile/', views.profile_settings, name='profile_settings'),

    # Shipping Address CRUD
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_create, name='address_create'),
    path('addresses/<int:pk>/edit/', views.address_update, name='address_update'),
    path('addresses/<int:pk>/delete/', views.address_delete, name='address_delete'),

    # Payment Method CRUD
    path('payment-methods/', views.payment_method_list, name='payment_method_list'),
    path('payment-methods/<int:pk>/delete/', views.payment_method_delete, name='payment_method_delete'),
    path('payment-methods/<int:pk>/set-default/', views.payment_method_set_default, name='payment_method_set_default'),
    
    # --- NEW WISH LIST URLS ---
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist_view, name='add_to_wishlist'),
    path('wishlist/remove/<int:item_id>/', views.remove_from_wishlist_view, name='remove_from_wishlist'),
]
