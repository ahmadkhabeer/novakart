from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from .models import UserProfile

User = get_user_model()

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fk_name = 'user'
    fields = ('address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'phone_number', 'profile_picture')

class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_phone_number')
    list_select_related = ('userprofile',)
    
    def get_phone_number(self, obj):
        try:
            return obj.userprofile.phone_number
        except UserProfile.DoesNotExist:
            return None
        
    get_phone_number.short_description = 'Phone Number'
    
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'city', 'country', 'profile_picture')
    search_fields = ('user__username', 'user__email', 'phone_number', 'city', 'country')
    raw_id_fields = ('user',)
