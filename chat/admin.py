from django.contrib import admin
from .models import SesiChat, PesanChat

@admin.register(SesiChat)
class SesiChatAdmin(admin.ModelAdmin):
    list_display = ('judul_chat', 'user', 'dokumen_terkait', 'dibuat_pada', 'diupdate_pada')
    list_filter = ('dibuat_pada', 'diupdate_pada')
    search_fields = ('judul_chat', 'user__username')

@admin.register(PesanChat)
class PesanChatAdmin(admin.ModelAdmin):
    list_display = ('sesi', 'pengirim', 'waktu_kirim')
    list_filter = ('pengirim', 'waktu_kirim')
    search_fields = ('isi_pesan', 'sesi__judul_chat')