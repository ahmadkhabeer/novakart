from django.shortcuts import render
from django.utils import timezone
from .models import Deal

def deal_list_view(request):
    """
    Displays a list of all currently active deals.
    """
    now = timezone.now()
    
    # Fetch all Deal objects that are active and within their start/end time.
    # Use select_related to also fetch the related Offer, Product, etc., in one efficient query.
    active_deals = Deal.objects.filter(
        is_active=True,
        start_time__lte=now,
        end_time__gte=now
    ).select_related(
        'offer__seller',
        'offer__variant__parent_product'
    )
    
    context = {
        'deals': active_deals
    }
    return render(request, 'promotions/deal_list.html', context)
