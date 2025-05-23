from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from .forms import fileDownloader
from .models import DownloadTask
import os, threading, queue, uuid
from yt_dlp import YoutubeDL

download_queue = queue.Queue()

def process_download():
    while True:
        task = download_queue.get()
        if task is None:  # Exit signal
            break
        link, path, task_id = task
        try:
            task_obj = DownloadTask.objects.get(task_id=task_id)
            task_obj.status = "In Progress"
            task_obj.save()

            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f'{path}/%(title)s.%(ext)s',
                'no-mtime': True
            }

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                title = info_dict.get('title', None)
                ext = info_dict.get('ext', None)
                original_file = os.path.join(path, f"{title}.{ext}")
                mp3_file = os.path.join(path, f"{title}.mp3")

                if os.path.exists(mp3_file):
                    task_obj.status = "File already exists"
                    task_obj.file_path = path
                    task_obj.title = title
                else:
                    ydl.download([link])
                    if os.path.exists(original_file):
                        os.rename(original_file, mp3_file)
                    task_obj.title = title
                    task_obj.status = "Completed"
                    task_obj.file_path = mp3_file
            task_obj.save()
        except Exception as e:
            task_obj.status = "Error"
            task_obj.error_message = str(e)
            task_obj.save()
        finally:
            download_queue.task_done()

@login_required
def status(request):
    tasks = DownloadTask.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'status.html', {"tasks": tasks})

@login_required
def get_task_status(request):
    tasks = DownloadTask.objects.filter(user=request.user).order_by('-created_at').values(
        'title', 'link', 'status', 'error_message', 'created_at', 'updated_at', 'file_path'
    )
    return JsonResponse(list(tasks), safe=False)

@login_required 
def index(request):
    if request.method == "POST":
        form = fileDownloader(request.POST)
        if form.is_valid():
            link = form.cleaned_data["link"]
            validator = URLValidator()
            try:
                validator(link)
                path = os.path.join(os.path.expanduser('~'), 'downloads')
                task_id = str(uuid.uuid4())
                # Associate the task with the current user
                DownloadTask.objects.create(
                    task_id=task_id,
                    link=link,
                    status="Queued",
                    user=request.user  # Make sure your model has a user field (ForeignKey)
                )
                download_queue.put((link, path, task_id))
                messages.info(request, f"Your download request has been added to the queue. Task ID: {task_id}")
                return redirect("status")
            except ValidationError:
                messages.error(request, "Invalid URL. Please provide a valid YouTube link.")
                return redirect("index")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect("index")

    form = fileDownloader()
    return render(request, 'index.html', {"form": form})

threading.Thread(target=process_download, daemon=True).start()