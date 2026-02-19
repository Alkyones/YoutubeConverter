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
            print("Starting new download processing thread")
            _processing_thread = threading.Thread(target=process_download, daemon=True)
            _processing_thread.start()
        else:
            print("Download processing thread is already running")

def process_download():
    while True:
        try:
            task = download_queue.get(timeout=30)  # Add timeout to prevent hanging
        except queue.Empty:
            continue
            
        if task is None:  # Exit signal
            break
            
        link, path, task_id, format_choice, quality_choice = task
        
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

            # Configure yt-dlp options based on format and quality
            def get_ydl_opts(format_type, quality, output_path):
                base_opts = {
                    'outtmpl': f'{output_path}/%(title)s.%(ext)s',
                    'no-mtime': True,
                    'writeinfojson': False,
                    'ignoreerrors': False,
                    'noplaylist': True,  # Only download single video, not playlist
                }
                
                if format_type == 'mp3':
                    # Audio only - download best audio and convert with pydub
                    base_opts['format'] = 'bestaudio/best'
                    # No postprocessors needed - we'll convert with pydub
                        
                else:  # mp4
                    # Video formats - more flexible with multiple fallbacks
                    if quality == 'low':
                        # Try progressively lower quality options
                        base_opts['format'] = 'worst[height<=480]/worst[height<=360]/worst[ext=mp4]/worst'
                    elif quality == 'high':
                        # Try high quality with fallbacks
                        base_opts['format'] = 'best[height<=1080][ext=mp4]/best[height<=1080]/best[height<=720][ext=mp4]/best[height<=720]/best[ext=mp4]/best'
                    else:  # medium
                        # Try medium quality with fallbacks  
                        base_opts['format'] = 'best[height<=720][ext=mp4]/best[height<=720]/best[height<=480][ext=mp4]/best[height<=480]/best[ext=mp4]/best'
                    
                return base_opts

            ydl_opts = get_ydl_opts(task_obj.format, task_obj.quality, path)
            print(f"Processing task {task_id}: {task_obj.format} {task_obj.quality}")
            print(f"yt-dlp options: {ydl_opts}")

            with YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(link, download=False)
                title = info_dict.get('title', None)
                
                # Clean title for filename - less aggressive cleaning
                import re
                # Remove only problematic characters for filenames, keep periods, parentheses etc.
                clean_title = re.sub(r'[<>:"/\|?*]', '', title).strip()
                print(f"Original title: {title}")
                print(f"Clean title: {clean_title}")
                
                # Determine file extension based on format and available formats
                expected_ext = 'mp3' if task_obj.format == 'mp3' else 'mp4'
                target_file = os.path.join(path, f"{clean_title}.{expected_ext}")
                
                print(f"Target file: {target_file}")

                if os.path.exists(target_file):
                    task_obj.status = "File already exists"
                    task_obj.file_path = target_file
                    task_obj.title = clean_title
                else:
                    print(f"Starting download for {link}")
                    ydl.download([link])
                    
                    # Handle MP3 conversion with pydub
                    if task_obj.format == 'mp3':
                        # Find the downloaded audio file in the directory
                        import glob
                        import time
                        
                        # Wait a moment for file system to update
                        time.sleep(1)
                        
                        # Look for any audio files with the clean title
                        patterns = [
                            os.path.join(path, f"{clean_title}.*"),
                            os.path.join(path, f"*{clean_title[-20:]}*"),  # Partial title match
                            os.path.join(path, "*.webm"),
                            os.path.join(path, "*.m4a"),
                            os.path.join(path, "*.opus")
                        ]
                        
                        downloaded_file = None
                        for pattern in patterns:
                            files = glob.glob(pattern)
                            if files:
                                # Get the most recently created file
                                downloaded_file = max(files, key=os.path.getctime)
                                break
                        
                        if downloaded_file:
                            print(f"Found downloaded file: {downloaded_file}")
                            
                            try:
                                # Convert to MP3 using pydub
                                from pydub import AudioSegment
                                
                                print(f"Converting {downloaded_file} to MP3...")
                                
                                # Load the audio file (pydub auto-detects format)
                                audio = AudioSegment.from_file(downloaded_file)
                                
                                # Set bitrate based on quality
                                bitrate = "192k" if task_obj.quality == 'high' else "128k" if task_obj.quality == 'medium' else "96k"
                                
                                # Export as MP3
                                audio.export(target_file, format="mp3", bitrate=bitrate)
                                
                                print(f"Successfully converted to MP3: {target_file}")
                                
                                # Remove original file if conversion successful and it's different
                                if os.path.exists(target_file) and downloaded_file != target_file:
                                    try:
                                        os.remove(downloaded_file)
                                        print(f"Removed original file: {downloaded_file}")
                                    except:
                                        print(f"Could not remove original file: {downloaded_file}")
                                
                            except ImportError:
                                print("pydub not available, using file rename method")
                                # Fallback: just rename the file
                                if downloaded_file != target_file:
                                    os.rename(downloaded_file, target_file)
                                    
                            except Exception as conv_error:
                                print(f"Conversion failed: {conv_error}")
                                # If conversion fails, rename the original file
                                if downloaded_file != target_file:
                                    try:
                                        os.rename(downloaded_file, target_file)
                                        print(f"Renamed original file to: {target_file}")
                                    except Exception as rename_error:
                                        print(f"Rename failed: {rename_error}")
                                        # Use the original file path as-is
                                        target_file = downloaded_file
                        else:
                            print("No downloaded audio file found!")
                            # This is an error condition
                            raise Exception("Download completed but no audio file found")
                    
                    else:  # MP4 download
                        # Find the downloaded MP4 file similar to MP3 logic
                        import glob
                        import time
                        
                        # Wait a moment for file system to update
                        time.sleep(1)
                        
                        # Look for MP4 files with various title patterns
                        patterns = [
                            os.path.join(path, f"{clean_title}.*"),
                            os.path.join(path, f"*{clean_title[-20:]}*"),  # Partial title match
                            os.path.join(path, "*.mp4"),
                            os.path.join(path, "*.mkv"),
                            os.path.join(path, "*.webm")
                        ]
                        
                        downloaded_file = None
                        for pattern in patterns:
                            files = glob.glob(pattern)
                            if files:
                                # Get the most recently created file
                                downloaded_file = max(files, key=os.path.getctime)
                                break
                        
                        if downloaded_file:
                            print(f"Found downloaded MP4 file: {downloaded_file}")
                            # Use the actual downloaded file path
                            target_file = downloaded_file
                        else:
                            print("No downloaded MP4 file found!")
                            raise Exception("Download completed but no MP4 file found")
                    
                    # Verify the file exists before marking as completed
                    if os.path.exists(target_file):
                        task_obj.title = clean_title
                        task_obj.status = "Completed"
                        task_obj.file_path = target_file
                        print(f"Download completed: {target_file}")
                    else:
                        raise Exception(f"Expected file not found: {target_file}")
            
            task_obj.save()
            
        except DownloadTask.DoesNotExist:
            print(f"Task with task_id {task_id} not found")
        except Exception as e:
            print(f"Error processing task {task_id}: {str(e)}")
            try:
                task_obj = DownloadTask.objects.get(task_id=task_id)
                task_obj.status = "Error"
                task_obj.error_message = str(e)
                task_obj.save()
                print(f"Updated task {task_id} with error status")
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
        'title', 'link', 'format', 'quality', 'status', 'error_message', 'created_at', 'updated_at', 'file_path'
    )
    return JsonResponse(list(tasks), safe=False)

def index(request):
    # Ensure processing thread is running every time someone accesses the page
    ensure_processing_thread()
    
    if request.method == "POST":
        form = fileDownloader(request.POST)
        if form.is_valid():
            link = form.cleaned_data["link"]
            format_choice = form.cleaned_data["format"]
            quality_choice = form.cleaned_data["quality"]
            validator = URLValidator()
            try:
                validator(link)
                
                # Check if URL is already being processed or completed recently
                existing_task = DownloadTask.objects.filter(
                    link=link, 
                    format=format_choice,
                    quality=quality_choice,
                    status__in=["Queued", "In Progress", "Completed"]
                ).first()
                
                if existing_task:
                    if existing_task.status == "Completed":
                        messages.info(request, f"This URL was already downloaded. Task ID: {existing_task.task_id}")
                    else:
                        messages.warning(request, f"This URL is already being processed. Task ID: {existing_task.task_id}")
                    return redirect("status")
                
                # Use media directory for consistency
                # Get the backend directory (parent of youtube app)
                from django.conf import settings
                path = os.path.join(settings.BASE_DIR, 'media')
                os.makedirs(path, exist_ok=True)
                task_id = str(uuid.uuid4())
                
                # Create the download task
                DownloadTask.objects.create(
                    task_id=task_id,
                    link=link,
                    format=format_choice,
                    quality=quality_choice,
                    status="Queued"
                )
                
                # Ensure processing thread is running
                ensure_processing_thread()
                
                # Add to queue
                download_queue.put((link, path, task_id, format_choice, quality_choice))
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
print("Initializing YouTube download processing thread...")
ensure_processing_thread()