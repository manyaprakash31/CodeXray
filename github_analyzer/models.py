from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

class AnalysisHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    repo_name = models.CharField(max_length=255)
    file_path = models.CharField(max_length=500)
    code = models.TextField()
    analysis = models.TextField()
    bug_analysis = models.TextField()
    chat_history = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.repo_name}/{self.file_path}"
