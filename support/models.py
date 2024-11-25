from django.db import models
from users.models import User

# Create your models here.
class Help(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='help_requests')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=[('open', 'Open'), ('closed', 'Closed')], default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Help Request by {self.user.username} - {self.status}"

    class Meta:
        verbose_name = "Help And Dispute"
        verbose_name_plural = "Help And Dispute"
        ordering = ['-created_at']  # Orders by `created_at` in descending order
       
