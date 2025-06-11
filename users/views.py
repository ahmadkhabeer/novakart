from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import ShippingAddress, PaymentMethod
from orders.models import Order
from .forms import UserRegisterForm, ShippingAddressForm, UserUpdateForm, ProfileUpdateForm

def register(request):
    """
    Handles new user registration.
    """
    if request.user.is_authenticated:
        return redirect('core:product_list')
        
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('users:login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard(request):
    """
    Main user dashboard showing recent orders and default address.
    """
    orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
    default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first()
    context = {
        'orders': orders,
        'default_address': default_address,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def profile_settings(request):
    """
    Allows user to update their account info (username, email) and profile details.
    """
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your account has been updated!')
            return redirect('users:profile_settings')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile_settings.html', context)

# --- Shipping Address Views ---

@login_required
def address_list(request):
    """
    Lists all shipping addresses for the current user.
    """
    addresses = ShippingAddress.objects.filter(user=request.user)
    return render(request, 'users/address_list.html', {'addresses': addresses})

@login_required
def address_create(request):
    """
    Handles creation of a new shipping address.
    """
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'New shipping address added.')
            # Redirect to the 'next' URL if it exists, otherwise to the address list
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            return redirect('users:address_list')
    else:
        form = ShippingAddressForm()
    return render(request, 'users/address_form.html', {'form': form, 'title': 'Add New Address'})

@login_required
def address_update(request, pk):
    """
    Handles updating an existing shipping address.
    """
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Address updated successfully.')
            return redirect('users:address_list')
    else:
        form = ShippingAddressForm(instance=address)
    return render(request, 'users/address_form.html', {'form': form, 'title': 'Edit Address'})

@login_required
def address_delete(request, pk):
    """
    Handles deletion of a shipping address after confirmation.
    """
    address = get_object_or_404(ShippingAddress, pk=pk, user=request.user)
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address has been deleted.')
        return redirect('users:address_list')
    return render(request, 'users/address_confirm_delete.html', {'address': address})

# --- Payment Method Views ---

@login_required
def payment_method_list(request):
    """
    Lists all saved payment methods for the current user.
    """
    payment_methods = PaymentMethod.objects.filter(user=request.user)
    return render(request, 'users/payment_method_list.html', {'payment_methods': payment_methods})

@login_required
def payment_method_delete(request, pk):
    """
    Handles deletion of a saved payment method.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    if payment_method.is_default:
        messages.error(request, "You cannot delete your default payment method.")
    else:
        payment_method.delete()
        messages.success(request, "Payment method deleted.")
    return redirect('users:payment_method_list')

@login_required
def payment_method_set_default(request, pk):
    """
    Sets a specific payment method as the default for the user.
    """
    payment_method = get_object_or_404(PaymentMethod, pk=pk, user=request.user)
    # The logic in the model's save() method handles unsetting other defaults.
    payment_method.is_default = True
    payment_method.save()
    messages.success(request, f"{payment_method} has been set as your default payment method.")
    return redirect('users:payment_method_list')


# --- Django Auth Class-Based Views ---

class UserLoginView(auth_views.LoginView):
    template_name = 'users/login.html'

class UserLogoutView(auth_views.LogoutView):
   # The default implementation is sufficient. next_page is set in urls.py
   pass

Sources
