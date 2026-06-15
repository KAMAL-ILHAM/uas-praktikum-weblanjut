from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('upload/', views.upload_view, name='upload'),
    
    # RUTE BARU: Menambahkan <int:pk> agar URL bisa menerima angka ID
    # Contoh hasilnya nanti: /documents/detail/1/ atau /documents/detail/15/
    path('detail/<int:pk>/', views.detail_view, name='detail'), 
    path('hapus/<int:doc_id>/', views.hapus_dokumen, name='hapus_dokumen'),

]