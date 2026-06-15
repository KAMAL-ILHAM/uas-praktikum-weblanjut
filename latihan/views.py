import json
import re
import random

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from documents.models import DokumenMateri
from documents.utils.ai_services import panggil_groq


@login_required(login_url='/auth/login/')
def generate_latihan(request):
    """Menghasilkan soal latihan (MCQ, Flashcard, Essay) menggunakan AI berdasarkan rangkuman dokumen."""
    if request.method == 'POST':
        # Pengambilan data dari request
        doc_id = request.POST.get('document_id')
        format_latihan = request.POST.get('format_latihan')
        jumlah = request.POST.get('jumlah_soal', 5)
        
        # Pengambilan dokumen referensi
        dokumen = get_object_or_404(DokumenMateri, id=doc_id, user=request.user)
        teks_materi = dokumen.rangkuman_ai
        
        # Seed acak untuk memastikan variasi hasil AI
        seed_acak = random.randint(1, 10000)
        
        # Penentuan prompt AI berdasarkan format latihan
        if format_latihan == 'pilihan_ganda':
            prompt = f"""
            Buat {jumlah} soal pilihan ganda (A,B,C,D) dari materi di bawah. 
            ATURAN WAJIB:
            1. ACAK fokus soalnya! Jangan gunakan soal yang sama dengan sebelumnya (Seed: {seed_acak}).
            2. Gali detail tersembunyi, jangan hanya bertanya konsep dasar di paragraf pertama.
            3. Variasikan letak kunci jawaban (jangan A terus atau C terus).
            Output HARUS JSON list murni (tanpa markdown): [{{"q": "..", "a": "..", "b": "..", "c": "..", "d": "..", "ans": "huruf_jawaban_saja"}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/mcq.html'
            
        elif format_latihan == 'flashcard':
            prompt = f"""
            Buat {jumlah} flashcard (tanya jawab singkat) dari materi di bawah.
            ATURAN WAJIB:
            1. ACAK istilah atau konsep yang diambil (Seed: {seed_acak}).
            2. Pilih konsep, studi kasus, atau definisi yang berbeda dan bervariasi.
            Output HARUS JSON list murni (tanpa markdown): [{{"front": "..", "back": ".."}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/flashcard.html'
            
        else:  # format_latihan == 'essay'
            prompt = f"""
            Buat {jumlah} soal essay analisis dari materi di bawah.
            ATURAN WAJIB:
            1. ACAK topik soalnya (Seed: {seed_acak}).
            2. VARIASIKAN GAYA PERTANYAAN SECARA EKSTRIM! Jangan monoton hanya menggunakan kata "Mengapa" atau "Bagaimana". 
               Gunakan berbagai tipe instruksi seperti: 
               - "Bandingkan A dan B..."
               - "Jelaskan perbedaan utama..."
               - "Berikan satu contoh penerapan..."
               - "Apa implikasi jika..."
               - "Evaluasi kelemahan dari..."
            3. SUPER PENTING: Tulis soal setajam dan sesingkat mungkin! MAKSIMAL 2 KALIMAT PENDEK. Jangan membuat skenario cerita bertele-tele. Langsung *to the point*.
            Output HARUS JSON list murni (tanpa markdown): [{{"soal": "..", "kunci": ".."}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/essay.html'

        # Eksekusi AI
        respons_ai = panggil_groq(prompt)
        
        # Parsing respons JSON dari AI
        try:
            clean_json = re.sub(r'```json|```', '', respons_ai).strip()
            data_latihan = json.loads(clean_json)
        except Exception as e:
            print(f"Error parsing JSON kuis: {e}")
            data_latihan = None

        # PERBAIKAN: Mengirimkan string JSON ter-serialize pada 'data' agar aman saat di-parse JavaScript
        return render(request, template_name, {
            'data': json.dumps(data_latihan),
            'data_safe': json.dumps(data_latihan),
            'dokumen': dokumen,
            'jumlah': jumlah
        })
            
    return redirect('users:dashboard')


@login_required(login_url='/auth/login/')
def evaluasi_essay_api(request):
    """Endpoint API untuk mengevaluasi jawaban essay user menggunakan AI."""
    if request.method == 'POST':
        try:
            data_body = json.loads(request.body)
            data_evaluasi = data_body.get('data_evaluasi', [])
            
            prompt = f"""
            TUGAS: Evaluasi jawaban ujian essay mahasiswa secara objektif.
            
            Berikut adalah data soal, jawaban mahasiswa, dan referensi jawaban AI yang ideal:
            {json.dumps(data_evaluasi, indent=2)}
            
            ATURAN:
            1. Berikan nilai (skor) dari 0 hingga 100 untuk setiap jawaban.
            2. Jika jawaban kosong atau sangat melenceng, beri skor 0.
            3. Berikan 'catatan' (feedback) singkat dan memotivasi untuk setiap jawaban.
            4. Output HARUS berupa JSON list murni, urutannya harus sama dengan urutan soal yang dikirim.
            
            FORMAT OUTPUT JSON:
            [
                {{"skor": 95, "catatan": "Analisis sangat tajam dan tepat sasaran."}},
                {{"skor": 40, "catatan": "Jawaban kurang lengkap, Anda melewatkan poin X."}}
            ]
            """
            
            respons_ai = panggil_groq(prompt)
            
            clean_json = re.sub(r'```json|```', '', respons_ai).strip()
            hasil_koreksi = json.loads(clean_json)
            
            return JsonResponse({
                'status': 'success',
                'hasil': hasil_koreksi
            })
            
        except Exception as e:
            print(f"Error API Evaluasi: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'invalid method'}, status=405)


# ==========================================
# Fallback / Static UI Views
# ==========================================

@login_required(login_url='/auth/login/')
def flashcard_view(request):
    return render(request, 'latihan/flashcard.html')


@login_required(login_url='/auth/login/')
def mcq_view(request):
    return render(request, 'latihan/mcq.html')


@login_required(login_url='/auth/login/')
def essay_view(request):
    return render(request, 'latihan/essay.html')