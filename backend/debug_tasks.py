#!/usr/bin/env python3
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cfe.settings')
django.setup()

from youtube.models import DownloadTask

print("=== Debug: Download Tasks Status ===")
tasks = DownloadTask.objects.all().order_by('-created_at')[:10]

if not tasks:
    print("No download tasks found.")
else:
    for task in tasks:
        print(f"Task ID: {task.task_id}")
        print(f"Title: {task.title}")
        print(f"Link: {task.link}")
        print(f"Format: {task.format}")
        print(f"Quality: {task.quality}")
        print(f"Status: {task.status}")
        print(f"File Path: {task.file_path}")
        if task.file_path and os.path.exists(task.file_path):
            print(f"File exists: YES ({os.path.getsize(task.file_path)} bytes)")
        else:
            print(f"File exists: NO")
        if task.error_message:
            print(f"Error: {task.error_message}")
        print(f"Created: {task.created_at}")
        print(f"Updated: {task.updated_at}")
        print("-" * 50)

# Check for any "In Progress" tasks and their status
in_progress = DownloadTask.objects.filter(status="In Progress")
if in_progress:
    print(f"\n=== Found {in_progress.count()} tasks still 'In Progress' ===")
    for task in in_progress:
        print(f"Task {task.task_id}: {task.title} - Created: {task.created_at}")
        
# Test pydub availability
try:
    from pydub import AudioSegment
    print("\n✅ pydub is available and working")
except ImportError:
    print("\n❌ pydub is not available")
except Exception as e:
    print(f"\n⚠️  pydub import error: {e}")

# Check download directory
download_path = os.path.join(os.getcwd(), 'media')
if os.path.exists(download_path):
    files = os.listdir(download_path)[:10]  # Show first 10 files
    print(f"\n=== Files in download directory ({len(files)} total) ===")
    for file in files:
        file_path = os.path.join(download_path, file)
        if os.path.isfile(file_path):
            size = os.path.getsize(file_path)
            print(f"{file} - {size} bytes")
else:
    print(f"\n⚠️  Download directory doesn't exist: {download_path}")