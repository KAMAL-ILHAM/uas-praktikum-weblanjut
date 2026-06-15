from django.contrib import admin
from .models import DokumenMateri

@admin.register(DokumenMateri)
class DokumenMateriAdmin(admin.ModelAdmin):
    # Menampilkan kolom-kolom penting di tabel depan
    list_display = ('judul_modul', 'user', 'mime_type', 'is_processed_ai', 'is_deleted', 'tanggal_unggah')
    
    # Filter canggih di sebelah kanan layar
    list_filter = ('is_processed_ai', 'is_deleted', 'mime_type', 'tanggal_unggah')
    
    # Kotak pencarian (Bisa cari judul dokumen atau nama mahasiswa)
    search_fields = ('judul_modul', 'deskripsi_singkat', 'user__username')