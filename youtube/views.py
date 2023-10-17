from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import HttpResponse
from .forms import fileDownloader

import os
import glob

from pytube import YouTube


def index(request):
    if request.method == "POST":
        form = fileDownloader(request.POST)
        if form.is_valid():
            link = form.cleaned_data["link"]
            yt = YouTube(link)
            video = yt.streams.filter(only_audio=True).first()

            path = os.path.join(os.path.expanduser('~'), 'downloads')
            f_search_name = str(video.title).split(' ')
            f_new = f_search_name[0] + '*' + f_search_name[-1] + '.*'
            if glob.glob(f"{path}//{f_new}"):
                messages.warning(request, "File already exists")
                return redirect(index)
                
            else:     
                out_file = video.download(output_path=os.path.join(os.path.expanduser('~'), 'downloads'))
                file_name = os.path.splitext(out_file)[0]+".mp3"
                os.rename(out_file, file_name)
            
                messages.success(request, "File downloaded.")
                return redirect(index)

    form = fileDownloader()
    return render(request, 'index.html', {"form": form})
