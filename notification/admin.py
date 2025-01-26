from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title','message', 'created_at','is_read')  # Fields displayed in the list view
    list_filter = ('created_at',)  # Add a comma to make this a tuple
    search_fields = ('user__username', 'title', 'message')  # Enable searching by these fields
