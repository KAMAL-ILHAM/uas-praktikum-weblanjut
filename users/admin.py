from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, SesiPerangkat


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    
    # Konfigurasi kolom yang ditampilkan pada tabel admin
    list_display = ['username', 'email', 'nama_instansi', 'tingkat_pendidikan', 'role', 'is_staff']
    
    # Kustomisasi grup field agar dapat diedit melalui form admin
    fieldsets = UserAdmin.fieldsets + (
        ('Profil Tampilan & Kontak', {
            'fields': ('foto_profil', 'bio', 'jenis_kelamin', 'tanggal_lahir', 'lokasi', 'nomor_telepon', 'alamat_lengkap')
        }),
        ('Informasi Pendidikan', {
            'fields': ('nomor_induk', 'nama_instansi', 'tingkat_pendidikan', 'bidang_studi')
        }),
        ('Hak Akses & Verifikasi', {
            'fields': ('role', 'is_email_verified', 'is_phone_verified', 'verification_token')
        }),
        ('Keamanan & Preferensi', {
            'fields': ('is_2fa_enabled', 'two_fa_method', 'is_biometric_enabled', 'notifikasi_aktif')
        }),
    )


# Registrasi model ke Django Admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SesiPerangkat)