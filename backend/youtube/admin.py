from django.contrib import admin
from .models import DownloadTask

@admin.register(DownloadTask)
class DownloadTaskAdmin(admin.ModelAdmin):
    list_display = ['task_id', 'title', 'format', 'quality', 'status', 'created_at', 'updated_at']
    list_filter = ['status', 'format', 'quality', 'created_at']
    search_fields = ['task_id', 'title', 'link']
    readonly_fields = ['task_id', 'created_at', 'updated_at']
