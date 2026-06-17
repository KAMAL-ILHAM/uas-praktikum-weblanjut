from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from .models import SesiChat, PesanChat
from documents.models import DokumenMateri
from documents.utils.ai_services import panggil_groq
from documents.utils.file_extractor import ekstrak_teks_dari_file

@login_required(login_url='/auth/login/')
def chat_view(request):
    """Menampilkan halaman utama chatbot dengan riwayat sesi."""
    riwayat_sesi = SesiChat.objects.filter(user=request.user).order_by('-dibuat_pada')
    return render(request, 'chat/chatbot.html', {'riwayat_sesi': riwayat_sesi})

@login_required(login_url='/auth/login/')
def get_chat_history_api(request, sesi_id):
    """Memuat riwayat pesan berdasarkan sesi yang dipilih dari sidebar."""
    try:
        sesi = SesiChat.objects.get(id=sesi_id, user=request.user)
        pesan_list = sesi.pesan.all()

        # Format sender ke lowercase untuk menyesuaikan class CSS di frontend
        data_pesan = [
            {
                'sender': p.pengirim.lower(),
                'teks': p.isi_pesan,
                'waktu': p.waktu_kirim.strftime('%H:%M')
            }
            for p in pesan_list
        ]

        return JsonResponse({
            'status': 'success',
            'judul': sesi.judul_chat,
            'pesan': data_pesan
        })

    except SesiChat.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan'}, status=404)

@login_required(login_url='/auth/login/')
def chatbot_api(request):
    """Memproses pengiriman pesan ke AI dan menangani lampiran file."""
    if request.method == 'POST':
        try:
            pesan_user = request.POST.get('pesan', '').strip()
            sesi_id = request.POST.get('sesi_id')
            doc_id = request.POST.get('doc_id')
            file_materi = request.FILES.get('file')

            # Skenario 1: Auto-load dari klik tombol chat di dashboard dokumen
            if pesan_user == '[INIT_DOC]' and doc_id:
                dokumen = get_object_or_404(DokumenMateri, id=doc_id, user=request.user)

                sesi = SesiChat.objects.create(
                    user=request.user,
                    judul_chat=f"Diskusi: {dokumen.judul_modul[:20]}",
                    dokumen_terkait=dokumen
                )

                balasan_ai = f"Dokumen **{dokumen.judul_modul}** telah saya pelajari. Apa yang ingin Anda tanyakan seputar materi ini?"
                PesanChat.objects.create(sesi=sesi, pengirim='AI', isi_pesan=balasan_ai)

                return JsonResponse({
                    'status': 'success',
                    'balasan': balasan_ai,
                    'sesi_id': sesi.id,
                    'judul': sesi.judul_chat
                })

            # Skenario 2: Alur percakapan reguler
            teks_tambahan = ""
            nama_file = ""

            # Penanganan lampiran file baru
            if file_materi:
                nama_file = file_materi.name
                try:
                    isi_dokumen = ekstrak_teks_dari_file(file_materi)
                    teks_tambahan = f"\n\n[DOKUMEN LAMPIRAN BARU DARI USER ({nama_file})]:\n{isi_dokumen}"
                except Exception as e:
                    return JsonResponse({'status': 'error', 'message': f'Gagal membaca file: {str(e)}'}, status=400)

            # Validasi input pesan dan file
            if not pesan_user and file_materi:
                pesan_user = f"Tolong berikan ringkasan dan bedah isi dokumen berikut: {nama_file}"
            elif not pesan_user and not file_materi:
                return JsonResponse({'status': 'error', 'message': 'Pesan tidak boleh kosong'}, status=400)

            # Pencarian sesi eksisting atau pembuatan sesi baru
            dokumen_terkait = None
            if sesi_id and sesi_id != 'null':
                sesi = SesiChat.objects.get(id=sesi_id, user=request.user)
                dokumen_terkait = sesi.dokumen_terkait
            else:
                judul_baru = pesan_user[:30] + "..." if len(pesan_user) > 30 else pesan_user
                sesi = SesiChat.objects.create(user=request.user, judul_chat=judul_baru)

            # Simpan pesan pengguna
            PesanChat.objects.create(sesi=sesi, pengirim='User', isi_pesan=pesan_user)

            # Injeksi konteks rangkuman dokumen ke memori AI jika tidak ada file baru
            if dokumen_terkait and not teks_tambahan:
                teks_tambahan = f"\n\n[INFO UNTUK AI - REFERENSI MATERI: {dokumen_terkait.judul_modul}]:\n{dokumen_terkait.rangkuman_ai}"

            # Persiapan prompt AI
            system_prompt = f"""
                        Kamu adalah “EIO AI”, asisten belajar dan rekan diskusi akademik khusus untuk platform EIO Master.

            ATURAN MUTLAK DAN BATASAN SISTEM (WAJIB DIPATUHI SESUAI URUTAN):
            1. FILTER KEAMANAN & ETIKA (PRIORITAS TERTINGGI): Jika pengguna meminta untuk belajar hal yang negatif, ilegal, berbahaya, atau melanggar norma/etika (seperti mencuri, meretas untuk kejahatan, menipu, dll), kamu WAJIB MENOLAKNYA. Jangan hanya memberikan penolakan singkat, tapi berikan nasihat dan saran yang mendidik layaknya seorang guru mengapa hal tersebut salah, lalu arahkan mereka untuk mempelajari hal yang positif.
            2. KATA KUNCI "BELAJAR": Jika topik AMAN dari Aturan 1 dan pengguna menggunakan kata "belajar", "mempelajari", atau "mengajarkan", kamu WAJIB MENJAWABNYA secara detail dan edukatif. Posisikan dirimu sebagai guru/tutor yang sedang memberikan materi panduan langkah demi langkah.
            3. ATURAN PENOLAKAN UMUM: Jika pengguna TIDAK menggunakan kata "belajar" dan menanyakan topik di luar materi akademik/pendidikan formal (seperti hiburan santai atau gosip), kamu WAJIB MENOLAK.
            4. KALIMAT TOLAKAN UMUM: Jika menolak karena melanggar Aturan 3, gunakan kalimat ini: "Maaf, saya adalah EIO AI khusus asisten belajar. Gunakan kata 'belajar' jika Anda ingin saya mengajarkan materi tersebut, atau tanyakan materi akademik lainnya."

            Pedoman jawaban saat merespons:
            - Berikan penjelasan yang terstruktur dan langsung ke inti pembahasan.
            - Gunakan format Markdown yang rapi (poin, heading, tebal, atau code block jika perlu).

            Pertanyaan/Instruksi User: {pesan_user}
            {teks_tambahan}
            """

            # Eksekusi AI dan simpan balasan
            balasan_ai = panggil_groq(system_prompt)
            PesanChat.objects.create(sesi=sesi, pengirim='AI', isi_pesan=balasan_ai)
            sesi.save()

            return JsonResponse({
                'status': 'success',
                'balasan': balasan_ai,
                'sesi_id': sesi.id,
                'judul': sesi.judul_chat
            })

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid'}, status=405)

# FUNGSI BARU: MENGHAPUS SESI CHAT PERMANEN DARI DATABASE
@login_required(login_url='/auth/login/')
def delete_chat_session_api(request, sesi_id):
    if request.method == 'POST':
        try:
            # Ambil sesi chat berdasarkan ID dan pastikan kepemilikannya cocok dengan user yang sedang login
            sesi = SesiChat.objects.get(id=sesi_id, user=request.user)
            sesi.delete() # Karena models cascading, data relasi di PesanChat otomatis ikut terhapus bersih
            return JsonResponse({'status': 'success', 'message': 'Riwayat obrolan berhasil dihapus permanent.'})
        except SesiChat.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan atau Anda tidak memiliki akses.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)

# FUNGSI BARU: MENGUBAH JUDUL (RENAME) SESI CHAT
@login_required(login_url='/auth/login/')
def rename_chat_session_api(request, sesi_id):
    """Memperbarui judul sesi chat berdasarkan input user."""
    if request.method == 'POST':
        try:
            # Ambil sesi chat dan pastikan kepemilikannya
            sesi = SesiChat.objects.get(id=sesi_id, user=request.user)

            # Ambil data judul baru dari request frontend
            judul_baru = request.POST.get('judul_baru', '').strip()

            if judul_baru:
                sesi.judul_chat = judul_baru
                sesi.save() # Simpan pembaruan ke database
                return JsonResponse({'status': 'success', 'message': 'Judul berhasil diperbarui.'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Judul tidak boleh kosong.'}, status=400)

        except SesiChat.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Sesi tidak ditemukan atau akses ditolak.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)