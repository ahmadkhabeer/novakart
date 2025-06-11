from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('cart/', include('carts.urls', namespace='carts')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('account/', include('users.urls', namespace='users')),
    path('promotions/', include('promotions.urls', namespace='promotions')),
    path('marketplace/', include('marketplace.urls', namespace='marketplace')),
    path('', include('core.urls', namespace='core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
