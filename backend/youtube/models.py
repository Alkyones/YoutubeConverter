from django.db import models

class DownloadTask(models.Model):
    task_id = models.CharField(max_length=255, unique=True)
    link = models.URLField()
    title = models.CharField(max_length=255, blank=True, null=True)
    format = models.CharField(max_length=10, default='mp3')
    quality = models.CharField(max_length=10, default='medium')
    status = models.CharField(max_length=50, default="Queued")
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    file_path = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Task {self.task_id}: {self.status}"
    
    class Meta:
        ordering = ['-created_at']