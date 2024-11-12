# urls.py
from django.urls import path
from .views import (
    create_chat_message,
    get_chat_messages_by_game
    
)

urlpatterns = [
    # Room URLs
    path('api/chat/', create_chat_message, name='create_chat_message'),
    path('api/chat/game/<int:game_id>/', get_chat_messages_by_game, name='chat-message-by-game'),
]
