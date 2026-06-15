from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from documents.models import DokumenMateri   # sesuaikan nama app kamu
from tasks.models import Tugas               # sesuaikan nama app kamu

# Inisialisasi Custom User Model
User = get_user_model()

# --- HALAMAN LOGIN ---
def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard') 

    if request.method == 'POST':
        usr = request.POST.get('username')
        psw = request.POST.get('password')

        user = authenticate(request, username=usr, password=psw)

        if user is not None:
            login(request, user)
            return redirect('users:dashboard') 
        else:
            messages.error(request, 'Username atau password salah! Silakan coba lagi.')

    return render(request, 'users/login.html')

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