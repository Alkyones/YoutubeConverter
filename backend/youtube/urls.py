from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('status/', views.status, name='status'),
    path('status/api/', views.get_task_status, name='get_task_status'),
]