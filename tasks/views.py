from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Tugas


@login_required(login_url='/auth/login/')
def task_list_view(request):
    """Menampilkan daftar tugas aktif dan menangani pembuatan tugas baru."""
    user = request.user
    sekarang = timezone.now()

    # Retensi Data: Menghapus tugas yang lebih tua dari 6 bulan (180 hari)
    batas_retensi = sekarang - timedelta(days=180)
    Tugas.objects.filter(user=user, tenggat_waktu__lt=batas_retensi).delete()

    if request.method == 'POST':
        nama = request.POST.get('nama_tugas')
        deadline = request.POST.get('deadline')
        kesulitan = request.POST.get('kesulitan')
        catatan = request.POST.get('catatan')
        gambar = request.FILES.get('task_image')
        
        if nama and deadline:
            Tugas.objects.create(
                user=user,
                nama_tugas=nama,
                tenggat_waktu=deadline,
                tingkat_kesulitan=kesulitan,
                catatan=catatan,
                lampiran_gambar=gambar,
                is_selesai=False
            )
            messages.success(request, "Tugas baru berhasil dijadwalkan!")
            return redirect('tasks:task_list')

    # Pengambilan data tugas aktif
    tugas_aktif = Tugas.objects.filter(user=user, is_selesai=False).order_by('tenggat_waktu')
    
    context = {
        'tugas_aktif': tugas_aktif,
        'total_tugas': tugas_aktif.count(),
    }
    return render(request, 'tasks/task_list.html', context)


@login_required(login_url='/auth/login/')
def task_calendar_view(request):
    """Menampilkan halaman arsip untuk tugas-tugas yang telah selesai."""
    user = request.user
    tugas_selesai = Tugas.objects.filter(user=user, is_selesai=True).order_by('-tenggat_waktu')
    
    context = {
        'tugas_selesai': tugas_selesai,
    }
    return render(request, 'tasks/task_calendar.html', context)


@login_required(login_url='/auth/login/')
def tandai_selesai(request, tugas_id):
    """Menandai tugas spesifik sebagai selesai (is_selesai=True) melalui request POST."""
    if request.method == 'POST':
        tugas = get_object_or_404(Tugas, id=tugas_id, user=request.user)
        tugas.is_selesai = True
        tugas.save()
        
        messages.success(request, f"Mantap! Tugas '{tugas.nama_tugas}' telah diselesaikan.")
        
    return redirect('tasks:task_list')

def set_pengingat_view(request, tugas_id):
    tugas = Tugas.objects.get(id=tugas_id)
    
    # Ambil waktu detik ini, lalu tambah 1 jam (hours=1)
    waktu_sekarang = timezone.now()
    tugas.waktu_pengingat = waktu_sekarang + timedelta(seconds=10)
    tugas.is_pengingat_terkirim = False # Reset statusnya
    
    tugas.save()
    messages.success(request, 'Pengingat berhasil disetel untuk 1 jam ke depan!')
    return redirect('users:dashboard')

def set_pengingat_satu_jam(request, tugas_id):
    # Mengambil data tugas berdasarkan ID dan User aktif
    tugas = Tugas.objects.get(id=tugas_id, user=request.user)
    
    # Set waktu pengingat 1 jam dari detik ini
    tugas.waktu_pengingat = timezone.now() + timedelta(seconds=10)
    tugas.is_pengingat_terkirim = False
    tugas.save()
    
    # Menggunakan nama_tugas sesuai struktur model terbaru
    messages.success(request, f'Pengingat untuk "{tugas.nama_tugas}" berhasil disetel 1 jam dari sekarang!')
    
    return redirect('users:dashboard')