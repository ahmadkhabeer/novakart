from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # --- Checkout Flow ---
    # Step 1: User reviews their cart and enters shipping info
    path('checkout/', views.checkout_view, name='checkout'),
    # Step 2: User confirms and is redirected to Paymob
    path('start-payment/', views.start_payment_view, name='start_payment'),
    # Step 3: Page shown after a successful webhook confirmation
    path('success/<int:order_id>/', views.order_success_view, name='order_success'),

    # --- Paymob Integration URLs ---
    # The server-to-server webhook Paymob calls to confirm payment
    path('payment/webhook/', views.payment_webhook, name='payment_webhook'),
    # The page the user's browser is redirected to after they finish paying on Paymob's site
    path('payment/processed/', views.payment_processed_callback, name='payment_processed_callback'),

    # --- Order History & Management ---
    path('history/', views.order_history_view, name='order_history'),
    path('history/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('history/<int:order_id>/return/', views.initiate_return_view, name='initiate_return'),
]
