from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('status/', views.status, name='status'),
    path('status/api/', views.get_task_status, name='get_task_status'),
    path('open-downloads/', views.open_downloads_folder, name='open_downloads_folder'),
]