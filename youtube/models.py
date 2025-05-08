from django.db import models

class DownloadTask(models.Model):
    task_id = models.CharField(max_length=100, unique=True)
    link = models.URLField()
    status = models.CharField(max_length=50, default="Queued")  # e.g., Queued, In Progress, Completed, Error
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_path = models.TextField(blank=True, null=True)  # New field to store the file path

    def __str__(self):
        return f"Task {self.task_id}: {self.status}"