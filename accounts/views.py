from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login

from django.contrib.auth.views import LoginView
from .forms import UserCreationForm, UserLoginForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        print(form.is_valid())
        print(form.errors)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login') 
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Log the user in
            return redirect('index')  # Redirect to the home page or any other page
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})