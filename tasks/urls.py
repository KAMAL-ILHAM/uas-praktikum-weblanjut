from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Daftar Tugas Aktif
    path('', views.task_list_view, name='task_list'),
    
    # Arsip & Kalender Tugas
    path('calendar/', views.task_calendar_view, name='task_calendar'),

    # Aksi Status Tugas
    path('selesai/<int:tugas_id>/', views.tandai_selesai, name='tandai_selesai'),
]