from django.core.exceptions import PermissionDenied
from .models import Seller

def seller_required(function):
    """
    Decorator to ensure that the user accessing the view is a registered seller.
    """
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'seller'):
            # This checks if the one-to-one reverse relationship exists.
            # A more basic check is Seller.objects.filter(user=request.user).exists()
            raise PermissionDenied
        return function(request, *args, **kwargs)
    
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
