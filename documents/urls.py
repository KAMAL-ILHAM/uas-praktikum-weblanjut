from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    path('detail/<int:pk>/', views.detail_view, name='detail'), 
    path('hapus/<int:doc_id>/', views.hapus_dokumen, name='hapus_dokumen'),

]