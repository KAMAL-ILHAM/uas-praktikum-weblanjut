from django.db import models
from django.conf import settings

class Tugas(models.Model):
    """Model untuk menyimpan jadwal dan detail tugas pengguna."""
    
    TINGKAT_KESULITAN_CHOICES = [
        ('Mudah', 'Mudah'),
        ('Sedang', 'Sedang'),
        ('Sulit', 'Sulit')
    ]
    
    # Relasi Utama
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tugas_user')
    
    # Detail Tugas
    nama_tugas = models.CharField(max_length=255)
    tenggat_waktu = models.DateTimeField()
    tingkat_kesulitan = models.CharField(max_length=10, choices=TINGKAT_KESULITAN_CHOICES, default='Sedang')
    catatan = models.TextField(blank=True, null=True)
    
    # Media & Status
    lampiran_gambar = models.ImageField(upload_to='tugas_lampiran/', blank=True, null=True)
    is_selesai = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    waktu_pengingat = models.DateTimeField(null=True, blank=True)
    is_pengingat_terkirim = models.BooleanField(default=False)

    def __str__(self):
        status = "Selesai" if self.is_selesai else "Aktif"
        return f"[{status}] {self.nama_tugas} - {self.user.username}"
    
    class Meta:
        verbose_name = "Tugas"
        verbose_name_plural = "Tugas"
        ordering = ['tenggat_waktu']  # Mengurutkan dari deadline paling dekat