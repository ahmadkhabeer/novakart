from django.urls import path
from . import views

app_name = 'carts'

urlpatterns = [
    # Carts homepage: /cart/
    path('', views.view_cart, name='view_cart'),

    # Action to add an item to the cart (from a product page)
    # e.g., POST to /cart/add/
    path('add/', views.add_to_cart, name='add_to_cart'),

    # Action to update an item's quantity
    # e.g., POST to /cart/items/123/update/
    path('items/<int:item_id>/update/', views.update_cart_item, name='update_cart_item'),

    # Action to remove an item from the cart
    # e.g., POST to /cart/items/123/remove/
    path('items/<int:item_id>/remove/', views.remove_from_cart, name='remove_from_cart'),

    # Action to move an active item to the "Saved for Later" list
    # e.g., POST to /cart/items/123/save/
    path('items/<int:item_id>/save/', views.save_for_later, name='save_for_later'),

    # Action to move a "Saved" item back to the active cart
    # e.g., POST to /cart/items/123/move-to-cart/
    path('items/<int:item_id>/move-to-cart/', views.move_to_cart, name='move_to_cart'),
]
