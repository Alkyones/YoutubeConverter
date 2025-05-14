from django.db import models
from django.contrib.auth.models import User
class DownloadTask(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    link = models.URLField()
    title = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=50, default="Queued")  # e.g., Queued, In Progress, Completed, Error
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_path = models.TextField(blank=True, null=True)  # New field to store the file path
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='download_tasks')

    def __str__(self):
        return f"Task {self.task_id}: {self.status}"