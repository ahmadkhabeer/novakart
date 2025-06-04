from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'shop/home.html', {"welcome_message":"Welcome to NovaKart 🛒"})