import os
import json
import re
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import DokumenMateri
from .utils.ai_services import generate_soal_mcq
from documents.utils.ai_services import buat_ringkasan
from documents.utils.file_extractor import ekstrak_teks_dari_file
from documents.utils.ai_services import panggil_groq

@login_required
def upload_view(request):
    if request.method == 'POST':
        judul = request.POST.get('judul_modul')
        deskripsi_singkat = request.POST.get('deskripsi_singkat')
        file_obj = request.FILES.get('file_dokumen')

        if not file_obj:
            messages.error(request, "Silakan pilih file dokumen terlebih dahulu!")
            return redirect('documents:upload')

        nama_file, ekstensi = os.path.splitext(file_obj.name)

        try:
            teks_mentah = ekstrak_teks_dari_file(file_obj)

            if not teks_mentah:
                messages.error(request, "Gagal membaca teks dari dokumen. Pastikan file tidak rusak.")
                return redirect('documents:upload')

            hasil_ringkasan = buat_ringkasan(teks_mentah)

            dokumen = DokumenMateri.objects.create(
                user=request.user,
                judul_modul=judul,
                deskripsi_singkat=deskripsi_singkat,
                file_dokumen=file_obj,
                rangkuman_ai=hasil_ringkasan,
                is_processed_ai=True,
                file_size=file_obj.size,
            )

            messages.success(request, f"Materi '{judul}' berhasil diunggah dan dirangkum oleh AI!")
            return redirect('documents:detail', pk=dokumen.pk)

        except Exception as e:
            messages.error(request, f"Terjadi kesalahan sistem: {str(e)}")
            return redirect('documents:upload')

    return render(request, 'documents/upload.html')

@login_required
def detail_view(request, pk):
    dokumen = get_object_or_404(DokumenMateri, pk=pk, user=request.user)
    context = {
        'dokumen': dokumen
    }
    return render(request, 'documents/detail.html', context)

@login_required
def generate_kuis_view(request, doc_id):
    if request.method == "POST":
        dokumen = get_object_or_404(DokumenMateri, id=doc_id)
        jumlah = request.POST.get('jumlah_soal', 5)
        
        daftar_soal = generate_soal_mcq(dokumen.rangkuman_ai, jumlah)
        
        return render(request, 'latihan/tampilan_kuis.html', {
            'daftar_soal': daftar_soal,
            'dokumen': dokumen
        })
    
@login_required(login_url='/auth/login/')
def hapus_dokumen(request, doc_id):
    if request.method == 'POST':
        dokumen = get_object_or_404(DokumenMateri, id=doc_id, user=request.user)
        nama_yang_dihapus = dokumen.judul_modul 
        
        dokumen.delete()
        messages.success(request, f"Dokumen '{nama_yang_dihapus}' berhasil dihapus.")
        
    return redirect('users:dashboard')

@login_required(login_url='/auth/login/')
def generate_latihan(request):
    if request.method == 'POST':
        doc_id = request.POST.get('document_id')
        format_latihan = request.POST.get('format_latihan')
        jumlah = request.POST.get('jumlah_soal', 5)
        
        dokumen = get_object_or_404(DokumenMateri, id=doc_id, user=request.user)
        teks_materi = dokumen.rangkuman_ai
        seed_acak = random.randint(1, 10000)
        
        if format_latihan == 'pilihan_ganda':
            prompt = f"""
            Buat {jumlah} soal pilihan ganda (A,B,C,D) dari materi di bawah. 
            ATURAN WAJIB:
            1. ACAK fokus soalnya! Jangan gunakan soal yang sama dengan sebelumnya (Seed: {seed_acak}).
            2. Variasikan letak kunci jawaban.
            Output HARUS JSON list murni: [{{'q': '..', 'a': '..', 'b': '..', 'c': '..', 'd': '..', 'ans': 'huruf_jawaban_saja'}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/mcq.html'
            
        elif format_latihan == 'flashcard':
            prompt = f"""
            Buat {jumlah} flashcard (tanya jawab singkat) dari materi di bawah.
            ATURAN WAJIB:
            1. ACAK istilah atau konsep yang diambil (Seed: {seed_acak}).
            Output HARUS JSON list murni: [{{'front': '..', 'back': '..'}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/flashcard.html'
            
        else: 
            prompt = f"""
            Buat {jumlah} soal essay analisis dari materi di bawah.
            ATURAN WAJIB:
            1. ACAK topik soalnya (Seed: {seed_acak}).
            2. VARIASIKAN GAYA PERTANYAAN!
            3. Tulis soal setajam dan sesingkat mungkin.
            Output HARUS JSON list murni: [{{'soal': '..', 'kunci': '..'}}] 
            Materi: {teks_materi}
            """
            template_name = 'latihan/essay.html'

        system_json = "Anda adalah sistem API. Hasilkan HANYA output berformat JSON list murni ([{...}]) tanpa teks pembuka, penutup, atau markdown apapun."
        respons_ai = panggil_groq(prompt, system_prompt=system_json)
        
        try:
            match = re.search(r'\[.*\]', respons_ai, re.DOTALL)
            if match:
                clean_json = match.group(0)
            else:
                clean_json = re.sub(r'```json|```', '', respons_ai).strip()
                
            data_latihan = json.loads(clean_json)
        except Exception as e:
            print(f"Error parsing JSON Groq: {e}\nRespons Asli AI: {respons_ai}")
            data_latihan = [] 

        return render(request, template_name, {
            'data': data_latihan,
            'dokumen': dokumen,
            'jumlah': jumlah
        })
            
    return redirect('users:dashboard')