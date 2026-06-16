# file: tasks/jobs.py

from django.utils import timezone
from django.core.mail import send_mail
from django.utils.html import strip_tags # Tambahkan ini untuk membuat versi teks biasa
from tasks.models import Tugas

def periksa_dan_kirim_pengingat():
    sekarang = timezone.now()
    
    # Filter tugas yang belum selesai, belum dikirim, dan waktunya sudah jatuh tempo
    tugas_jatuh_tempo = Tugas.objects.filter(
        is_selesai=False,
        is_pengingat_terkirim=False,
        waktu_pengingat__lte=sekarang
    )
    
    for tugas in tugas_jatuh_tempo:
        subject = f'Pengingat Tugas: {tugas.nama_tugas}' 
        
        # === KODE HTML UNTUK EMAIL ===
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
                    <h3 style="margin-top: 0;">Halo, {tugas.user.username}!</h3>
                    <p>Ini adalah pengingat otomatis bahwa Anda memiliki tugas yang harus segera diselesaikan sebelum tenggat waktu berakhir.</p>
                    
                    <div class="task-box">
                        <div class="task-label">NAMA TUGAS</div>
                        <div class="task-name">{tugas.nama_tugas}</div>
                    </div>
                    
                    <p>Jangan tunda pekerjaanmu. Segera selesaikan dan perbarui status tugas ini di dashboard.</p>
                    
                    <div style="text-align: center; margin-top: 30px;">
                        <a href="http://127.0.0.1:8000/auth/login/" class="btn-login">Buka Dashboard</a>
                    </div>
                </div>
                <div class="footer">
                    <p style="margin: 0;">Email ini dikirim secara otomatis oleh sistem EIO Master.<br>Mohon tidak membalas email ini.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Versi plain-text untuk aplikasi email yang tidak mendukung HTML
        plain_message = strip_tags(html_message)
        
        try:
            send_mail(
                subject=subject,
                message=plain_message, # Pesan fallback
                from_email='noreply@eiomaster.com',
                recipient_list=[tugas.user.email],
                html_message=html_message, # <--- TAMBAHKAN PARAMETER INI
                fail_silently=False,
            )
            
            tugas.is_pengingat_terkirim = True
            tugas.save()
            print(f"✅ Berhasil mengirim email pengingat HTML: {tugas.nama_tugas}")
            
        except Exception as e:
            print(f"❌ Gagal mengeksekusi pengingat otomatis: {e}")