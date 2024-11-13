from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal info', {'fields': ('user_type', 'image', 'device_token', 'address', 'visible_to_user', 'twitter_url', 'instagram_url', 'facebook_url')}),
        ('Permissions', {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'password1', 'password2'),
        }),
    )
    list_display = (
        'id', 'username', 'device_token', 'otp_code', 'verify', 'email', 'user_type', 'is_active', 
        'is_staff', 'is_superuser', 'full_name', 'address', 'longitude', 'latitude', 'Trade_radius',
        'visible_to_user', 'twitter_url', 'instagram_url', 'facebook_url'
    )
    list_filter = ('user_type', 'is_active', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(User, UserAdmin)
