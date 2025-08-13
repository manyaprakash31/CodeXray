from django.db import models
from django.contrib.auth.models import User

class DebugHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    input_code = models.TextField()
    corrected_code = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Debug by {self.user.username} at {self.created_at}"
