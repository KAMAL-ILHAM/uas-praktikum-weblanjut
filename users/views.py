import random 
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.utils.html import strip_tags

from documents.models import DokumenMateri   
from tasks.models import Tugas               

# Inisialisasi Custom User Model
User = get_user_model()

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard') 

    if request.method == 'POST':
        usr = request.POST.get('username')
        psw = request.POST.get('password')

        user = authenticate(request, username=usr, password=psw)

        if user is not None:
            # === LOGIKA BARU UNTUK 2FA ===
            if user.is_2fa_enabled and user.two_fa_method == 'email':
                # 1. Generate 6 digit angka acak
                otp_code = str(random.randint(100000, 999999))
                
                # 2. Simpan OTP dan ID user di session sementara
                request.session['pending_user_id'] = user.id
                request.session['2fa_otp'] = otp_code
                
                # 3. Kirim email HTML via Mailtrap
                subject = 'Kode Keamanan (OTP) Login - EIO Master'
                
                # === KODE HTML UNTUK EMAIL OTP ===
                html_message = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; }}
                        .email-container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
                        .header {{ background: linear-gradient(135deg, #8160ff, #633cf5); padding: 30px 20px; text-align: center; color: white; }}
                        .header h2 {{ margin: 0; font-size: 24px; font-weight: 800; letter-spacing: 1px; }}
                        .content {{ padding: 35px 30px; color: #334155; line-height: 1.6; text-align: center; }}
                        .otp-box {{ background-color: #f8fafc; border: 2px dashed #cbd5e1; padding: 20px; margin: 30px auto; border-radius: 12px; width: fit-content; min-width: 200px; }}
                        .otp-code {{ font-size: 36px; font-weight: 800; color: #633cf5; letter-spacing: 10px; margin: 0; }}
                        .warning-text {{ font-size: 13px; color: #ef4444; font-weight: 600; margin-top: 25px; padding: 10px; background: #fef2f2; border-radius: 8px; display: inline-block; }}
                        .footer {{ background-color: #f8fafc; padding: 20px; text-align: center; font-size: 13px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                        <div class="header">
                            <h2>EIO MASTER</h2>
                        </div>
                        <div class="content">
                            <h3 style="margin-top: 0; color: #1e293b; font-size: 20px;">Verifikasi Login Anda</h3>
                            <p>Halo, <strong>{user.username}</strong>!</p>
                            <p>Kami mendeteksi percobaan login ke akun Anda. Silakan masukkan 6 digit kode keamanan (OTP) di bawah ini untuk melanjutkan:</p>
                            
                            <div class="otp-box">
                                <p class="otp-code">{otp_code}</p>
                            </div>
                            
                            <div class="warning-text">
                                ⚠️ PENTING: Kode ini bersifat rahasia. Jangan berikan kepada siapapun!
                            </div>
                        </div>
                        <div class="footer">
                            <p style="margin: 0; margin-bottom: 8px;">Jika Anda tidak merasa melakukan login, abaikan email ini atau segera ubah kata sandi Anda.</p>
                            <p style="margin: 0;">&copy; EIO Master System</p>
                        </div>
                    </div>
                </body>
                </html>
                """
                
                # Versi fallback teks biasa
                plain_message = strip_tags(html_message)
                
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email='noreply@eiomaster.com',
                    recipient_list=[user.email],
                    html_message=html_message, # <--- Wajib dipasang agar HTML ter-render
                    fail_silently=False,
                )
                
                # 4. Arahkan ke halaman input OTP
                messages.info(request, 'Kode OTP telah dikirim ke email Anda.')
                return redirect('users:verify_otp')
            
            else:
                # Jika 2FA mati, langsung login normal seperti biasa
                login(request, user)
                return redirect('users:dashboard') 
        else:
            messages.error(request, 'Username atau password salah! Silakan coba lagi.')

    return render(request, 'users/login.html')

# --- HALAMAN VERIFIKASI OTP ---
def verify_otp_view(request):
    # Jika tidak ada sesi pending login, lempar kembali ke halaman login
    if 'pending_user_id' not in request.session:
        return redirect('users:login')

    if request.method == 'POST':
        input_otp = request.POST.get('otp_code')
        saved_otp = request.session.get('2fa_otp')
        user_id = request.session.get('pending_user_id')

        # Cek apakah OTP yang diketik sama dengan yang dikirim ke email
        if input_otp == saved_otp:
            user = User.objects.get(id=user_id)
            login(request, user) # Baru login-kan user-nya di sini!
            
            # Hapus jejak OTP dari session demi keamanan
            del request.session['pending_user_id']
            del request.session['2fa_otp']
            
            messages.success(request, 'Verifikasi berhasil. Selamat datang!')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Kode OTP salah atau tidak valid!')

    return render(request, 'users/verify_otp.html')

def password_reset_success_view(request):
    logout(request) 
    
    return render(request, 'password_reset_success.html')

# --- HALAMAN REGISTRASI ---
def register_view(request):
    if request.method == 'POST':
        username_input = request.POST.get('username')
        email_input = request.POST.get('email')
        password_input = request.POST.get('password')
        confirm_password_input = request.POST.get('confirm_password')

        if password_input != confirm_password_input:
            messages.error(request, 'Password dan Konfirmasi Password tidak cocok!')
            return redirect('users:register')

        if User.objects.filter(email=email_input).exists():
            messages.error(request, 'Email ini sudah terdaftar. Silakan gunakan email lain!')
            return redirect('users:register')

        if User.objects.filter(username=username_input).exists():
            messages.error(request, 'Username sudah dipakai. Cari nama lain ya!')
            return redirect('users:register')

        user = User.objects.create_user(
            username=username_input, 
            email=email_input, 
            password=password_input
        )
        user.save()

        messages.success(request, 'Akun berhasil dibuat! Silakan Login.')
        return redirect('users:login')

    return render(request, 'users/register.html')

# --- HALAMAN DASHBOARD ---
@login_required
def dashboard_view(request):
    # --- LOGIKA MATERI ---
    doc_type = request.GET.get('type', 'all')
    sort_materi = request.GET.get('sort', 'terbaru')
    
    dokumen = DokumenMateri.objects.filter(user=request.user)
    
    if doc_type != 'all':
        # Filter berdasarkan ekstensi file di database
        dokumen = dokumen.filter(file_dokumen__icontains=doc_type)
        
    order_materi = '-tanggal_unggah' if sort_materi == 'terbaru' else 'tanggal_unggah'
    dokumen_terbaru = dokumen.order_by(order_materi)

    # --- LOGIKA TUGAS ---
    difficulty = request.GET.get('difficulty', 'all')
    sort_tugas = request.GET.get('sort_tugas', 'terdekat')
    
    tugas = Tugas.objects.filter(user=request.user, is_selesai=False)
    
    if difficulty != 'all':
        tugas = tugas.filter(tingkat_kesulitan=difficulty)
        
    order_tugas = 'tenggat_waktu' if sort_tugas == 'terdekat' else '-tenggat_waktu'
    tugas_aktif = tugas.order_by(order_tugas)

    return render(request, 'users/dashboard.html', {
        'dokumen_terbaru': dokumen_terbaru,
        'tugas_aktif': tugas_aktif,
    })

@login_required
def task_list_view(request):
    user = request.user
    
    # Menangkap permintaan urutan dari form dropdown
    sort_by = request.GET.get('sort', 'terdekat')

    # Logika pengurutan berdasarkan tenggat waktu (deadline)
    if sort_by == 'terjauh':
        # Urutkan dari deadline yang paling lama (pakai minus)
        tugas_aktif = Tugas.objects.filter(user=user, is_selesai=False, is_archived=False).order_by('-tenggat_waktu')
    else:
        # Default: Terdekat (yang paling mendesak)
        tugas_aktif = Tugas.objects.filter(user=user, is_selesai=False, is_archived=False).order_by('tenggat_waktu')

    context = {
        'tugas_aktif': tugas_aktif,
    }
    return render(request, 'users/task_list.html', context)

# --- HALAMAN PENGATURAN (Sistem Multi-Tab) ---
@login_required
def settings_view(request):
    user = request.user

    if request.method == 'POST':
        action = request.POST.get('action') # Cek tab mana yang sedang disubmit

        # --- TAB 1: EDIT PROFIL ---
        if action == 'edit_profil':
            if 'foto_profil' in request.FILES:
                user.foto_profil = request.FILES['foto_profil']
            
            user.username = request.POST.get('username', user.username)
            user.bio = request.POST.get('bio', user.bio)
            user.jenis_kelamin = request.POST.get('jenis_kelamin', user.jenis_kelamin)
            
            # Cek tanggal lahir agar tidak error format jika input dikosongkan
            tgl_lahir = request.POST.get('tanggal_lahir')
            if tgl_lahir:
                user.tanggal_lahir = tgl_lahir
                
            user.nama_instansi = request.POST.get('institusi', user.nama_instansi)
            user.lokasi = request.POST.get('lokasi', user.lokasi)
            
            user.save()
            messages.success(request, 'Profil publik berhasil diperbarui!')
            return redirect('users:settings')
        
        elif action == 'toggle_notif':
            # Jika dicentang, HTML akan mengirim nilai 'on'. Jika dimatikan, nilainya kosong.
            status = request.POST.get('status_notif')
            
            if status == 'on':
                request.user.is_pengingat_aktif = True
                messages.success(request, 'Fitur pengingat diaktifkan!')
            else:
                request.user.is_pengingat_aktif = False
                messages.warning(request, 'Fitur pengingat telah disembunyikan.')
                
            request.user.save()
            return redirect('users:settings') # Sesuaikan dengan nama URL settings kamu

        # --- TAB 2: INFORMASI PRIBADI ---
        elif action == 'informasi_pribadi':
            # Pecah nama lengkap jadi First Name dan Last Name bawaan Django
            nama_lengkap = request.POST.get('nama_lengkap', '')
            if ' ' in nama_lengkap:
                user.first_name, user.last_name = nama_lengkap.split(' ', 1)
            else:
                user.first_name = nama_lengkap
                user.last_name = ''

            user.email = request.POST.get('email', user.email)
            user.nomor_telepon = request.POST.get('nomor_telepon', user.nomor_telepon)
            user.alamat_lengkap = request.POST.get('alamat_lengkap', user.alamat_lengkap)
            
            user.save()
            messages.success(request, 'Informasi pribadi berhasil disimpan!')
            return redirect('users:settings')

        # --- TAB 3: KATA SANDI & AUTENTIKASI ---
        elif action == 'keamanan':
            # .strip() berguna untuk menghapus spasi kosong jika user hanya mengetik spasi
            old_password = request.POST.get('old_password', '').strip()
            new_password = request.POST.get('new_password', '').strip()
            confirm_password = request.POST.get('confirm_password', '').strip()

            password_changed = False
            
            # Jika user MENGETIK SESUATU di salah satu kolom password
            if old_password or new_password or confirm_password:
                # Cegah user yang hanya mengisi 1 kolom tapi mengosongkan yang lain
                if not old_password or not new_password or not confirm_password:
                    messages.error(request, 'Harap isi SEMUA kolom password jika ingin mengubahnya!')
                    return redirect('users:settings')
                
                if not user.check_password(old_password):
                    messages.error(request, 'Password lama Anda salah!')
                    return redirect('users:settings')
                
                if new_password != confirm_password:
                    messages.error(request, 'Password baru dan konfirmasi tidak cocok!')
                    return redirect('users:settings')
                
                user.set_password(new_password)
                update_session_auth_hash(request, user) # Pertahankan sesi login
                password_changed = True

            # Tangkap status 2FA dari form (Centang = True, Kosong = False)
            is_2fa_enabled_form = request.POST.get('is_2fa_enabled') == 'on'
            two_fa_method_form = request.POST.get('two_fa_method', user.two_fa_method)

            # Cek apakah status 2FA atau Metode-nya BENAR-BENAR berubah dari database
            two_fa_changed = (user.is_2fa_enabled != is_2fa_enabled_form) or (user.two_fa_method != two_fa_method_form)

            # Jika ADA perubahan (Password diganti ATAU 2FA digeser/diubah)
            if password_changed or two_fa_changed:
                user.is_2fa_enabled = is_2fa_enabled_form
                user.two_fa_method = two_fa_method_form
                user.save()
                messages.success(request, 'Pengaturan keamanan berhasil diperbarui!')
            else:
                # Jika tombol diklik tapi tidak ada yang disentuh/diubah sama sekali
                messages.info(request, 'Tidak ada perubahan yang dilakukan pada pengaturan keamanan.')

            return redirect('users:settings')

    return render(request, 'users/settings.html')

@login_required
def dashboard_view(request):
    # Ambil parameter tab dari URL, defaultnya 'materi'
    active_tab = request.GET.get('active_tab', 'materi')
    
    # --- LOGIKA MATERI ---
    doc_type = request.GET.get('type', 'all')
    sort_materi = request.GET.get('sort', 'terbaru')
    dokumen = DokumenMateri.objects.filter(user=request.user)
    if doc_type != 'all':
        dokumen = dokumen.filter(file_dokumen__icontains=doc_type)
    order_materi = '-tanggal_unggah' if sort_materi == 'terbaru' else 'tanggal_unggah'
    dokumen_terbaru = dokumen.order_by(order_materi)

    # --- LOGIKA TUGAS ---
    difficulty = request.GET.get('difficulty', 'all')
    sort_tugas = request.GET.get('sort_tugas', 'terdekat')
    tugas = Tugas.objects.filter(user=request.user, is_selesai=False)
    if difficulty != 'all':
        tugas = tugas.filter(tingkat_kesulitan=difficulty)
    order_tugas = 'tenggat_waktu' if sort_tugas == 'terdekat' else '-tenggat_waktu'
    tugas_aktif = tugas.order_by(order_tugas)

    return render(request, 'users/dashboard.html', {
        'dokumen_terbaru': dokumen_terbaru,
        'tugas_aktif': tugas_aktif,
        'active_tab': active_tab, # <--- Tambahkan ini
    })

# --- FITUR LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('users:login')