from django.contrib.auth.models import AbstractUser
from django.db import models
import os


def user_profile_path(instance, filename):
    """Menentukan path upload dinamis untuk foto profil pengguna."""
    return f'users/{instance.username}/profile/{filename}'


class CustomUser(AbstractUser):
    # Konfigurasi Choices (Dropdown)
    TINGKAT_PENDIDIKAN_CHOICES = [
        ('Pelajar', 'Pelajar (SD / SMP / SMA / SMK)'),
        ('Mahasiswa', 'Mahasiswa (D3 / S1 / S2)'),
    ]
    
    GENDER_CHOICES = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
        ('O', 'Rahasia/Lainnya'),
    ]
    
    TWO_FA_METHODS = [
        ('email', 'OTP via Email'),
        ('sms', 'OTP via SMS'),
        ('app', 'Aplikasi Authenticator'),
    ]
    
    ROLE_CHOICES = [
        ('Admin', 'Administrator'),
        ('User', 'Pengguna Standar')
    ]

    # Profil Tampilan Publik
    foto_profil = models.ImageField(upload_to=user_profile_path, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    jenis_kelamin = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    tanggal_lahir = models.DateField(null=True, blank=True)
    lokasi = models.CharField(max_length=100, blank=True, null=True)

    # Data Akademik
    nomor_induk = models.CharField(max_length=25, unique=True, blank=True, null=True, help_text="Masukkan NISN / NIS / NIM")
    nama_instansi = models.CharField(max_length=150, blank=True, null=True, help_text="Nama Sekolah atau Universitas")
    tingkat_pendidikan = models.CharField(max_length=15, choices=TINGKAT_PENDIDIKAN_CHOICES, default='Pelajar')
    bidang_studi = models.CharField(max_length=100, blank=True, null=True, help_text="Contoh: IPA, RPL, Teknik Informatika")

    # Informasi Pribadi & Verifikasi
    nomor_telepon = models.CharField(max_length=20, blank=True, null=True)
    alamat_lengkap = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='User')
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)

    # Kata Sandi, Autentikasi & Preferensi
    last_password_change = models.DateTimeField(blank=True, null=True)
    is_2fa_enabled = models.BooleanField(default=False)
    two_fa_method = models.CharField(max_length=10, choices=TWO_FA_METHODS, default='email')
    is_biometric_enabled = models.BooleanField(default=False)
    notifikasi_aktif = models.BooleanField(default=True)

    def __str__(self):
        instansi = self.nama_instansi if self.nama_instansi else "Instansi Belum Diisi"
        return f"{self.username} - {instansi}"


class SesiPerangkat(models.Model):
    """Model untuk mencatat sesi login dan informasi perangkat aktif."""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sesi_login')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    sistem_operasi = models.CharField(max_length=100)
    browser = models.CharField(max_length=100)
    terakhir_aktif = models.DateTimeField(auto_now=True)
    is_aktif = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.sistem_operasi} ({self.browser})"
    
    class Meta:
        verbose_name = "Sesi Perangkat"
        verbose_name_plural = "Sesi Perangkat"