from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.db.models import Count
from .forms import fileDownloader
from .models import DownloadTask
import os, threading, queue, uuid, time
from yt_dlp import YoutubeDL

download_queue = queue.Queue()
_processing_thread = None
_thread_lock = threading.Lock()
_task_locks = {}  # Dictionary to track tasks being processed

def ensure_processing_thread():
    """Ensure only one processing thread is running"""
    global _processing_thread
    with _thread_lock:
        if _processing_thread is None or not _processing_thread.is_alive():
            _processing_thread = threading.Thread(target=process_download, daemon=True)
            _processing_thread.start()

def process_download():
    while True:
        try:
            task = download_queue.get(timeout=30)  # Add timeout to prevent hanging
        except queue.Empty:
            continue
            
        if task is None:  # Exit signal
            break
            
        link, path, task_id = task
        
        # Prevent duplicate processing of same task
        if task_id in _task_locks:
            continue
            
        _task_locks[task_id] = True
        
        try:
            # Use task_id (string UUID) instead of id to find the task
            task_obj = DownloadTask.objects.get(task_id=task_id)
            
            # Skip if already processing or completed
            if task_obj.status in ["In Progress", "Completed", "File already exists", "Error"]:
                continue
                
            task_obj.status = "In Progress"
            task_obj.save()

            # Ensure download directory exists
            os.makedirs(path, exist_ok=True)

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{path}/%(title)s.%(ext)s',
                'no-mtime': True
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                title = info_dict.get('title', None)
                ext = info_dict.get('ext', None)
                
                # Clean title for filename
                clean_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                original_file = os.path.join(path, f"{clean_title}.{ext}")
                mp3_file = os.path.join(path, f"{clean_title}.mp3")

                if os.path.exists(mp3_file):
                    task_obj.status = "File already exists"
                    task_obj.file_path = mp3_file
                    task_obj.title = clean_title
                else:
                    ydl.download([link])
                    if os.path.exists(original_file):
                        os.rename(original_file, mp3_file)
                    task_obj.title = clean_title
                    task_obj.status = "Completed"
                    task_obj.file_path = mp3_file
            
            task_obj.save()
            
        except DownloadTask.DoesNotExist:
            print(f"Task with task_id {task_id} not found")
        except Exception as e:
            try:
                task_obj = DownloadTask.objects.get(task_id=task_id)
                task_obj.status = "Error"
                task_obj.error_message = str(e)
                task_obj.save()
                print(f"Error processing task {task_id}: {str(e)}")
            except Exception as save_error:
                print(f"Error updating task {task_id}: {str(save_error)}")
        finally:
            # Remove task from processing locks
            _task_locks.pop(task_id, None)
            download_queue.task_done()

def status(request):
    tasks = DownloadTask.objects.all().order_by('-created_at')
    return render(request, 'status.html', {"tasks": tasks})

def get_task_status(request):
    tasks = DownloadTask.objects.all().order_by('-created_at').values(
        'title', 'link', 'status', 'error_message', 'created_at', 'updated_at', 'file_path'
    )
    return JsonResponse(list(tasks), safe=False)

def index(request):
    if request.method == "POST":
        form = fileDownloader(request.POST)
        if form.is_valid():
            link = form.cleaned_data["link"]
            validator = URLValidator()
            try:
                validator(link)
                
                # Check if URL is already being processed or completed recently
                existing_task = DownloadTask.objects.filter(
                    link=link, 
                    status__in=["Queued", "In Progress", "Completed"]
                ).first()
                
                if existing_task:
                    if existing_task.status == "Completed":
                        messages.info(request, f"This URL was already downloaded. Task ID: {existing_task.task_id}")
                    else:
                        messages.warning(request, f"This URL is already being processed. Task ID: {existing_task.task_id}")
                    return redirect("status")
                
                path = os.path.join(os.path.expanduser('~'), 'downloads')
                task_id = str(uuid.uuid4())
                
                # Create the download task
                DownloadTask.objects.create(
                    task_id=task_id,
                    link=link,
                    status="Queued"
                )
                
                # Ensure processing thread is running
                ensure_processing_thread()
                
                # Add to queue
                download_queue.put((link, path, task_id))
                messages.success(request, f"Download request added to queue. Task ID: {task_id}")
                return redirect("status")
                
            except ValidationError:
                messages.error(request, "Invalid URL. Please provide a valid YouTube link.")
                return redirect("index")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect("index")

    form = fileDownloader()
    return render(request, 'index.html', {"form": form})

# Start initial processing thread
ensure_processing_thread()