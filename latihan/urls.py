from django.urls import path
from . import views

app_name = 'latihan'

urlpatterns = [
    # Fungsi Generator Latihan
    path('generate/', views.generate_latihan, name='generate'),
    
    # Endpoint API (Evaluasi AI)
    path('api/evaluasi-essay/', views.evaluasi_essay_api, name='api_evaluasi_essay'),
    
    # Tampilan Antarmuka (UI Views)
    path('flashcard/', views.flashcard_view, name='flashcard'),
    path('mcq/', views.mcq_view, name='mcq'),
    path('essay/', views.essay_view, name='essay'),
]