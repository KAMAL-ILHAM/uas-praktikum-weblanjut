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