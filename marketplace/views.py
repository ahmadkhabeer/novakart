from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages
from .models import Seller
from .forms import SellerRegisterForm

@login_required
def seller_register_view(request):
    """
    Handles the process for a regular user to become a seller.
    """
    # Check if the user is already a seller
    if Seller.objects.filter(user=request.user).exists():
        messages.info(request, "You are already registered as a seller.")
        return redirect('users:dashboard') # Redirect them to their dashboard

    if request.method == 'POST':
        form = SellerRegisterForm(request.POST)
        if form.is_valid():
            try:
                # Get the 'Sellers' group
                sellers_group = Group.objects.get(name='Sellers')
            except Group.DoesNotExist:
                # This is a fallback in case the group wasn't created in the admin
                messages.error(request, "A critical error occurred: The 'Sellers' user group does not exist. Please contact support.")
                return redirect('core:product_list')

            # Create the seller profile but don't save to the database yet
            seller = form.save(commit=False)
            seller.user = request.user # Assign the current user
            seller.save()

            # Add the user to the 'Sellers' group
            request.user.groups.add(sellers_group)

            messages.success(request, "Congratulations! You are now registered as a seller on NovaKart.")
            return redirect('users:dashboard') # Redirect to dashboard after successful registration
    else:
        form = SellerRegisterForm()

    context = {
        'form': form
    }
    return render(request, 'marketplace/seller_register.html', context)
