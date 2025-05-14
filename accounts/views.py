from django.shortcuts import render, redirect
from django.contrib.auth import login as auth_login
from .forms import UserCreationForm, UserLoginForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            return redirect('index')  # Redirect to home after registration
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user is not None:
                auth_login(request, user)
                return redirect('index')
            else:
                form.add_error(None, "Invalid username/email or password.")
    else:
        form = UserLoginForm()
    return render(request, 'registration/login.html', {'form': form})