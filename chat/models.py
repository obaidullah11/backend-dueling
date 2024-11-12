# models.py
from django.db import models
from users.models import User
from Tournaments.models import Game


from django.db import models
from users.models import User
from Tournaments.models import Game

class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="room")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.message[:20]}..."
