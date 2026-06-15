from django.contrib import admin
from .models import (
    SesiLatihan, SoalFlashcard, SoalMCQ, SoalEssay, 
    HasilLatihan, PilihanMCQ, RekamFlashcard, RekamEssay, RekamMCQ
)

# ==========================================
# MASTER KUIS
# ==========================================
@admin.register(SesiLatihan)
class SesiLatihanAdmin(admin.ModelAdmin):
    list_display = ('user', 'format_latihan', 'dokumen', 'jumlah_soal', 'dibuat_pada')
    list_filter = ('format_latihan', 'dibuat_pada')
    search_fields = ('user__username', 'dokumen__judul_modul')

# ==========================================
# BANK SOAL
# ==========================================
@admin.register(SoalFlashcard)
class SoalFlashcardAdmin(admin.ModelAdmin):
    list_display = ('id', 'sesi', 'sisi_depan')
    search_fields = ('sisi_depan', 'sisi_belakang')

@admin.register(SoalMCQ)
class SoalMCQAdmin(admin.ModelAdmin):
    list_display = ('id', 'sesi', 'pertanyaan')
    search_fields = ('pertanyaan',)

@admin.register(PilihanMCQ)
class PilihanMCQAdmin(admin.ModelAdmin):
    list_display = ('soal', 'teks_pilihan', 'is_benar')
    list_filter = ('is_benar',)
    search_fields = ('teks_pilihan',)

@admin.register(SoalEssay)
class SoalEssayAdmin(admin.ModelAdmin):
    list_display = ('id', 'sesi', 'batas_kata')
    search_fields = ('pertanyaan',)

# ==========================================
# LAPORAN & REKAM JEJAK
# ==========================================
@admin.register(HasilLatihan)
class HasilLatihanAdmin(admin.ModelAdmin):
    list_display = ('user', 'sesi_latihan', 'skor_total', 'jumlah_benar', 'jumlah_salah', 'tanggal_selesai')
    list_filter = ('tanggal_selesai',)
    search_fields = ('user__username',)

@admin.register(RekamFlashcard)
class RekamFlashcardAdmin(admin.ModelAdmin):
    list_display = ('hasil', 'kartu', 'status_ingat')
    list_filter = ('status_ingat',)

@admin.register(RekamMCQ)
class RekamMCQAdmin(admin.ModelAdmin):
    list_display = ('hasil', 'soal', 'jawaban_user')

@admin.register(RekamEssay)
class RekamEssayAdmin(admin.ModelAdmin):
    list_display = ('hasil', 'soal')