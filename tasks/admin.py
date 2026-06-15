from django.contrib import admin
from .models import Tugas

@admin.register(Tugas)
class TugasAdmin(admin.ModelAdmin):
    """Konfigurasi tampilan tabel dan filter untuk model Tugas di Django Admin."""
    
    list_display = ('nama_tugas', 'user', 'tenggat_waktu', 'tingkat_kesulitan', 'is_selesai', 'is_archived')
    list_filter = ('is_selesai', 'is_archived', 'tingkat_kesulitan', 'tenggat_waktu')
    search_fields = ('nama_tugas', 'catatan', 'user__username')