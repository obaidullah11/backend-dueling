from django.contrib import admin
from .models import Help

@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_user_type', 'description', 'status', 'created_at')  # Include user_type
    list_filter = ('status',)
    search_fields = ('user__username', 'description')

    def get_user_type(self, obj):
        """Retrieve the user_type from the related User model."""
        return obj.user.user_type if hasattr(obj.user, 'user_type') else 'N/A'
    get_user_type.short_description = 'User Type'
