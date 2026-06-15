from django.db import models
from django.conf import settings
from documents.models import DokumenMateri


class SesiLatihan(models.Model):
    FORMAT_CHOICES = [
        ('Flashcard', 'Flashcard Pintar'),
        ('MCQ', 'Pilihan Ganda'),
        ('Essay', 'Essay')
    ]
    
    # Relasi Utama
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sesi_latihan')
    dokumen = models.ForeignKey(DokumenMateri, on_delete=models.CASCADE, related_name='latihan_dokumen')
    
    # Pengaturan Latihan
    format_latihan = models.CharField(max_length=20, choices=FORMAT_CHOICES)
    jumlah_soal = models.IntegerField(default=10)
    durasi_waktu_menit = models.IntegerField(blank=True, null=True, help_text="Durasi pengerjaan kuis dalam menit untuk timer UI")
    
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_format_latihan_display()} ({self.dokumen.judul_modul}) - {self.user.username}"
    
    class Meta:
        verbose_name = "Sesi Latihan"
        verbose_name_plural = "Sesi Latihan"


# ==========================================
# BANK SOAL
# ==========================================

class SoalFlashcard(models.Model):
    sesi = models.ForeignKey(SesiLatihan, on_delete=models.CASCADE, related_name='soal_flashcard')
    sisi_depan = models.TextField(help_text="Pertanyaan atau Terminologi")
    sisi_belakang = models.TextField(help_text="Jawaban atau Penjelasan")

    def __str__(self):
        return f"Flashcard - Sesi {self.sesi.id}"
    
    class Meta:
        verbose_name = "Soal Flashcard"
        verbose_name_plural = "Soal Flashcard"


class SoalMCQ(models.Model):
    KUNCI_CHOICES = [
        ('A', 'Opsi A'),
        ('B', 'Opsi B'),
        ('C', 'Opsi C'),
        ('D', 'Opsi D'),
    ]
    
    sesi = models.ForeignKey(SesiLatihan, on_delete=models.CASCADE, related_name='soal_mcq')
    pertanyaan = models.TextField()
    
    # Opsi Jawaban
    opsi_a = models.CharField(max_length=255, null=True, blank=True)
    opsi_b = models.CharField(max_length=255, null=True, blank=True)
    opsi_c = models.CharField(max_length=255, null=True, blank=True)
    opsi_d = models.CharField(max_length=255, null=True, blank=True)
    
    # Kunci Jawaban
    jawaban_benar = models.CharField(max_length=1, choices=KUNCI_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"MCQ - Sesi {self.sesi.id}: Kunci {self.jawaban_benar}"
    
    class Meta:
        verbose_name = "Soal MCQ"
        verbose_name_plural = "Soal MCQ"


class SoalEssay(models.Model):
    sesi = models.ForeignKey(SesiLatihan, on_delete=models.CASCADE, related_name='soal_essay')
    pertanyaan = models.TextField()
    batas_kata = models.IntegerField(default=500, help_text="Batas maksimal kata untuk jawaban")

    def __str__(self):
        return f"Essay - Sesi {self.sesi.id}"
    
    class Meta:
        verbose_name = "Soal Essay"
        verbose_name_plural = "Soal Essay"


# ==========================================
# LAPORAN & REKAM JEJAK
# ==========================================

class HasilLatihan(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='riwayat_hasil')
    sesi_latihan = models.OneToOneField(SesiLatihan, on_delete=models.CASCADE, related_name='hasil')
    
    # Data Evaluasi
    skor_total = models.IntegerField(default=0, help_text="Nilai akhir skala 0-100")
    jumlah_benar = models.IntegerField(default=0)
    jumlah_salah = models.IntegerField(default=0)
    
    waktu_pengerjaan_asli = models.DurationField(blank=True, null=True) 
    tanggal_selesai = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Hasil {self.user.username} - Skor: {self.skor_total}"
    
    class Meta:
        verbose_name = "Hasil Latihan"
        verbose_name_plural = "Hasil Latihan"


class PilihanMCQ(models.Model):
    soal = models.ForeignKey(SoalMCQ, on_delete=models.CASCADE, related_name='pilihan')
    teks_pilihan = models.CharField(max_length=255)
    is_benar = models.BooleanField(default=False)

    def __str__(self):
        status = "Jawaban Benar" if self.is_benar else "Salah"
        return f"[{status}] {self.teks_pilihan}"
    
    class Meta:
        verbose_name = "Pilihan MCQ"
        verbose_name_plural = "Pilihan MCQ"


class RekamFlashcard(models.Model):
    hasil = models.ForeignKey(HasilLatihan, on_delete=models.CASCADE, related_name='detail_flashcard')
    kartu = models.ForeignKey(SoalFlashcard, on_delete=models.CASCADE)
    
    # Status Evaluasi Pengguna
    status_ingat = models.BooleanField(default=False)

    def __str__(self):
        status = "Ingat" if self.status_ingat else "Lupa"
        return f"Kartu {self.kartu.id} - {status}"
    
    class Meta:
        verbose_name = "Rekam Flashcard"
        verbose_name_plural = "Rekam Flashcard"


class RekamEssay(models.Model):
    hasil = models.ForeignKey(HasilLatihan, on_delete=models.CASCADE, related_name='detail_essay')
    soal = models.ForeignKey(SoalEssay, on_delete=models.CASCADE)
    
    # Data Input Pengguna
    teks_jawaban = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Jawaban Essay untuk Soal {self.soal.id}"
    
    class Meta:
        verbose_name = "Rekam Essay"
        verbose_name_plural = "Rekam Essay"


class RekamMCQ(models.Model):
    hasil = models.ForeignKey(HasilLatihan, on_delete=models.CASCADE, related_name='detail_mcq')
    soal = models.ForeignKey(SoalMCQ, on_delete=models.CASCADE)
    
    # Data Input Pengguna
    jawaban_user = models.CharField(max_length=1, choices=SoalMCQ.KUNCI_CHOICES, blank=True, null=True)

    def __str__(self):
        jawab = self.jawaban_user if self.jawaban_user else "Tidak Dijawab"
        return f"Soal {self.soal.id} - Dijawab: {jawab}"
    
    class Meta:
        verbose_name = "Rekam MCQ"
        verbose_name_plural = "Rekam MCQ"