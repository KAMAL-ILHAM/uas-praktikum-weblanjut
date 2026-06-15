import os
import re
import json
import markdown
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def panggil_groq(prompt_text, system_prompt="Anda adalah EIO AI, tutor pintar yang ahli merangkum materi secara edukatif dengan format Markdown yang rapi."):
    api_key = os.getenv("GROQ_API_KEY")
    
    if not api_key:
        return "Gagal menghubungi AI: GROQ_API_KEY tidak ditemukan di file .env"

    batas_karakter = 35000
    if len(prompt_text) > batas_karakter:
        prompt_text = prompt_text[:batas_karakter] + "\n\n[INFO SISTEM: SISA TEKS DOKUMEN DIPOTONG KARENA MELEBIHI KAPASITAS MEMORI API...]"

    client = OpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key
    )
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_text}
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Gagal menghubungi AI: {str(e)}"

def buat_ringkasan(teks_dokumen):
    prompt = f"""
    TUGAS: Analisis materi berikut dan buat ringkasan yang edukatif.
    
    ATURAN FORMAT:
    1. JANGAN gunakan label seperti 'INTRO', 'POIN PENTING', atau 'KESIMPULAN'.
    2. Gunakan bahasa Indonesia yang komunikatif (gaya bahasa tutor).
    3. Jika ada perbandingan data atau alat, WAJIB sajikan dalam format TABEL MARKDOWN standar.
    4. JANGAN gunakan simbol pagar (#) untuk judul, gunakan huruf tebal saja.
    
    MATERI:
    {teks_dokumen}
    """
    
    hasil_mentah = panggil_groq(prompt)
    
    if hasil_mentah.startswith("Gagal menghubungi AI:"):
        return hasil_mentah
    
    hasil_bersih = re.sub(r'^(INTRO|POIN PENTING|KESIMPULAN|TABEL):?\s*', '', hasil_mentah, flags=re.IGNORECASE | re.MULTILINE)
    hasil_bersih = hasil_bersih.replace('#', '')    
    
    hasil_html = markdown.markdown(hasil_bersih, extensions=['tables', 'fenced_code', 'nl2br'])    
    return hasil_html

def generate_soal_mcq(teks_materi, jumlah=5):
    prompt = f"""
    TUGAS: Buat {jumlah} soal pilihan ganda berdasarkan materi di bawah.
    FORMAT OUTPUT: Harus JSON murni (list of dictionaries) dengan key: 
    'pertanyaan', 'opsi_a', 'opsi_b', 'opsi_c', 'opsi_d', 'jawaban_benar'.
    
    MATERI:
    {teks_materi}
    """
    
    system_json_prompt = "Anda adalah sistem API pembuat soal. Hasilkan HANYA output berformat JSON murni tanpa teks pembuka, penutup, atau penjelasan apapun."
    
    respons = panggil_groq(prompt, system_prompt=system_json_prompt)
    
    try:
        clean_json = respons.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return None