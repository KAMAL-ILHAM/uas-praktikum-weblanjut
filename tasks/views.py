from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.utils.html import strip_tags
from django.conf import settings
from django.core.mail import send_mail
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
    tugas = Tugas.objects.get(id=tugas_id, user=request.user)

    # 1. Update Database
    tugas.waktu_pengingat = timezone.now() + timedelta(seconds=10)
    tugas.is_pengingat_terkirim = True
    tugas.save()

    # 2. Siapkan Desain Email HTML (Diambil dari jobs.py milikmu)
    subject = f"PENGINGAT EIO: Tugas '{tugas.nama_tugas}'"
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; }}
            .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
            .header {{ background: linear-gradient(135deg, #8160ff, #633cf5); padding: 30px 20px; text-align: center; color: white; }}
            .header h2 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 1px; }}
            .content {{ padding: 30px; color: #334155; line-height: 1.6; }}
            .task-box {{ background-color: #f1f5f9; border-left: 4px solid #633cf5; padding: 15px 20px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
            .task-name {{ font-size: 18px; font-weight: 700; color: #1e293b; margin: 0; }}
            .task-label {{ font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 5px; }}
            .btn-login {{ display: inline-block; background-color: #633cf5; color: #ffffff !important; text-decoration: none; padding: 12px 25px; border-radius: 8px; font-weight: bold; margin-top: 10px; }}
            .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 13px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <h2>EIO MASTER</h2>
            </div>
            <div class="content">
                <h3 style="margin-top: 0;">Halo, {request.user.username}!</h3>
                <p>Ini adalah pengingat otomatis bahwa Anda memiliki tugas yang harus segera diselesaikan sebelum tenggat waktu berakhir.</p>

                <div class="task-box">
                    <div class="task-label">NAMA TUGAS</div>
                    <div class="task-name">{tugas.nama_tugas}</div>
                </div>

                <p>Jangan tunda pekerjaanmu. Segera selesaikan dan perbarui status tugas ini di dashboard.</p>

                <div style="text-align: center; margin-top: 30px;">
                    <a href="http://eio.pythonanywhere.com/auth/login/" class="btn-login">Buka Dashboard</a>
                </div>
            </div>
            <div class="footer">
                <p style="margin: 0;">Email ini dikirim secara otomatis oleh sistem EIO Master.<br>Mohon tidak membalas email ini.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_message = strip_tags(html_message)
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [request.user.email]

    # 3. Eksekusi Pengiriman
    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=email_from,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )
        messages.success(request, f'Pengingat email HTML untuk "{tugas.nama_tugas}" telah meluncur ke {request.user.email}!')
    except Exception as e:
        messages.error(request, f'Gagal mengirim email: {str(e)}')

    return redirect('users:dashboard')