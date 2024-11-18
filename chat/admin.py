from django.contrib import admin
from .models import ChatMessage
@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'message', 'timestamp')  # Fields to display in the list view
    search_fields = ('message', 'user__username', 'game__name')  # Fields to search by in the admin search bar
    list_filter = ('game', 'user')  # Filters to apply in the list view

