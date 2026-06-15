from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

# FUNGSI VALIDASI MAKSIMAL 10 MB (Gunakan nama validate_file_size)
def validate_file_size(value):
    limit = 10 * 1024 * 1024 # 10 MB dalam bytes
    if value.size > limit:
        raise ValidationError('File terlalu besar! Ukuran maksimal adalah 10 MB.')

class DokumenMateri(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dokumen_user')
    judul_modul = models.CharField(max_length=255)
    deskripsi_singkat = models.CharField(max_length=255, blank=True, null=True)
    
    # --- PENERAPAN VALIDATOR DI SINI ---
    file_dokumen = models.FileField(
        upload_to='materi_dokumen/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'ppt', 'pptx']),
            validate_file_size  # <-- Panggil dengan nama yang SAMA PERSIS
        ],
        help_text="Format yang diizinkan: PDF, DOC/DOCX, PPT/PPTX. Maksimal 10 MB."
    )
    
    mime_type = models.CharField(max_length=50, blank=True, null=True)
    file_size = models.PositiveIntegerField(blank=True, null=True)
    is_processed_ai = models.BooleanField(default=False)
    rangkuman_ai = models.TextField(blank=True, null=True)
    tanggal_unggah = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.judul_modul} - {self.user.username}"