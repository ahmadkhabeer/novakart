from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    """
    Stores additional user-specific information not covered by Django's
    default Auth_User model, such as addresses and phone numbers.
    It has a one-to-one relationship with the Auth_User table.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,
                                help_text='One-to-one relationship with the Auth_User table.')
    address_line_1 = models.CharField(max_length=255, blank=True, null=True, 
                                        help_text="First line of the user's default address.")
    address_line_2 = models.CharField(max_length=255, blank=True, null=True,
                                        help_text="Second line of the user's default address.")
    city = models.CharField(max_length=255, blank=True, null=True,
                            help_text="City of the user's default address.")
    state = models.CharField(max_length=100, blank=True, null=True,
                             help_text="State of the user's default address.")
    postal_code = models.CharField(max_length=20, blank=True, null=True,
                                   help_text="Postal code of the user's default address.")
    country = models.CharField(max_length=100, blank=True, null=True,
                               help_text="Country of the user's default address.")
    phone_number = models.CharField(max_length=20, blank=True, null=True,
                                    help_text="User's phone number.")
    profile_picture = models.ImageField(upload_to='profile_pics/$Y/$m/$d', blank=True,
                                        null=True, help_text="Path to the user's profile picture file.")
    
    def __str__(self):
        return f'Profile for {self.user.username}'