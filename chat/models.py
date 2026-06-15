from django.db import models
from django.conf import settings
from documents.models import DokumenMateri

class SesiChat(models.Model):
    # Relasi
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sesi_chat')
    dokumen_terkait = models.ForeignKey(DokumenMateri, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_dokumen')
    
    # Data Sesi
    judul_chat = models.CharField(max_length=255, default="Percakapan Baru")
    context_summary = models.TextField(blank=True, null=True, help_text="Ringkasan konteks obrolan (Memory AI) untuk menghemat token")
    
    # Timestamps
    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diupdate_pada = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.judul_chat} - {self.user.username}"
    
    class Meta:
        verbose_name = "Sesi Chat"
        verbose_name_plural = "Sesi Chat"
        ordering = ['-diupdate_pada']


class PesanChat(models.Model):
    PENGIRIM_CHOICES = [
        ('User', 'Pengguna'),
        ('AI', 'EIO AI')
    ]
    
    sesi = models.ForeignKey(SesiChat, on_delete=models.CASCADE, related_name='pesan')
    pengirim = models.CharField(max_length=10, choices=PENGIRIM_CHOICES)
    isi_pesan = models.TextField()
    waktu_kirim = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.pengirim}] pada {self.waktu_kirim.strftime('%H:%M')} (Sesi: {self.sesi.id})"
    
    class Meta:
        verbose_name = "Pesan Chat"
        verbose_name_plural = "Pesan Chat"
        ordering = ['waktu_kirim']