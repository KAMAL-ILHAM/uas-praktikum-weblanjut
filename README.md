# EIO Task & Chat Management System

EIO Task & Chat Management System merupakan aplikasi web berbasis Django yang dikembangkan sebagai proyek UAS Praktikum Web Lanjut. Aplikasi ini menyediakan fitur manajemen tugas, autentikasi pengguna, sistem chat, serta integrasi AI untuk membantu pengguna dalam mengelola aktivitas dan komunikasi secara efisien.

## Live Demo

Aplikasi dapat diakses melalui:

https://eio.pythonanywhere.com/

---

## Fitur

- Autentikasi pengguna (Login dan Logout)
- Manajemen pengguna
- Manajemen tugas (Create, Read, Update, Delete)
- Sistem chat antar pengguna
- Integrasi AI menggunakan Groq API
- Manajemen dokumen dan media

---

## Teknologi yang Digunakan

| Teknologi | Keterangan |
|------------|------------|
| Python | Bahasa pemrograman utama |
| Django | Framework web |
| MySQL | Database Management System |
| HTML, CSS, Bootstrap | Antarmuka pengguna |
| Groq API | Integrasi AI |
| Git & GitHub | Version Control |
| PythonAnywhere | Deployment Hosting |

---

# Instalasi

## 1. Clone Repository

```bash
git clone https://github.com/USERNAME/NAMA_REPOSITORY.git
cd NAMA_REPOSITORY
```

## 2. Membuat Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependency

```bash
pip install -r requirements.txt
```

## 4. Membuat Database MySQL

Masuk ke MySQL kemudian jalankan perintah berikut:

```sql
CREATE DATABASE eio_db;
```

## 5. Konfigurasi Environment Variable

Buat file `.env` pada direktori utama project dan isi dengan konfigurasi berikut:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=eio_db
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=127.0.0.1
DB_PORT=3306

GROQ_API_KEY=your-groq-api-key
```

### Mendapatkan Groq API Key

1. Buka https://console.groq.com/
2. Login atau buat akun.
3. Buat API Key baru.
4. Salin API Key ke variabel `GROQ_API_KEY`.

## 6. Menjalankan Migrasi Database

```bash
python manage.py migrate
```

## 7. Membuat Akun Administrator (Opsional)

```bash
python manage.py createsuperuser
```

## 8. Menjalankan Server

```bash
python manage.py runserver
```

Buka browser dan akses:

```text
http://127.0.0.1:8000/
```

---

# Struktur Project

```text
├── chat/
├── documents/
├── latihan/
├── locale/
├── media/
├── tasks/
├── templates/
├── users/
├── UAS_praktikum_weblanjut_kelompok11/
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

---

# Deployment

Aplikasi telah dideploy menggunakan PythonAnywhere dan dapat diakses melalui:

https://eio.pythonanywhere.com/

---

# Pengembang

Kelompok 11  
Praktikum Web Lanjut  