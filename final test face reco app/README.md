# Aplikasi API Pengenalan Wajah dengan Flask dan Google Cloud Storage

Aplikasi ini adalah API berbasis Flask untuk mengenali dan mendaftarkan wajah, menggunakan DeepFace dan Google Cloud Storage (GCS) sebagai database gambar wajah.

## Fitur
- Sinkronisasi otomatis database wajah dari GCS
- Endpoint `/recognize` untuk mengenali wajah
- Endpoint `//validate_face_image` untuk mendeteksi dari gambar apakah ada wajah yang dapat dideteksi
- Endpoint `/register` untuk mendaftarkan wajah baru
- Dukungan client Python (bisa diintegrasikan ke robot Pepper)

---

## Prasyarat
- **Python 3.10**
- **Google Cloud Service Account** dan file credential (lihat di bawah)
- **Bucket GCS** untuk database gambar wajah

---

## Setup Aman untuk Public Repo

### 1. **JANGAN upload file `key.json` ke repo!**
- File `key.json` sudah ada di `.gitignore`.
- Hanya upload `key.json.example` (isi dummy, bukan credential asli).

### 2. **Semua variabel sensitif diatur lewat environment variable**
- Nama bucket, path credential, dan BASE_URL **tidak di-hardcode** di kode.
- Semua script Python mengambil variabel berikut dari environment:
  - `GCS_BUCKET_NAME` (nama bucket GCS)
  - `GOOGLE_APPLICATION_CREDENTIALS` (path ke file credential, default: `key.json`)
  - `BASE_URL` (alamat server API, default: `http://localhost:8000`)

### 3. **Contoh file credential**
- File `key.json.example` sudah tersedia. Copy ke `key.json` dan isi dengan credential asli milikmu.

---

## Cara Setup (Local Development)

1. **Clone repo dan masuk ke folder project**
2. **Copy file credential**
   ```sh
   cp key.json.example key.json
   # Lalu edit dan isi dengan credential asli
   ```
3. **Set environment variable** (Linux/macOS)
   ```sh
   export GCS_BUCKET_NAME=your-bucket-name
   export GOOGLE_APPLICATION_CREDENTIALS=key.json
   export BASE_URL=http://localhost:8000
   ```
   (Windows: gunakan `set` atau `.env` sesuai shell yang dipakai)
4. **Buat dan aktifkan virtual environment**
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Jalankan server**
   ```sh
   python app.py
   # atau untuk production:
   gunicorn --bind 127.0.0.1:8000 app:app
   ```
6. **Jalankan client/test**
   - Edit `BASE_URL` di environment variable jika perlu.
   - Jalankan `test_client.py` atau integrasikan ke robot Pepper dengan `pepper_client.py`.

---

## Cara Deploy ke Compute Engine (Cloud)

1. **Copy project ke VM** (pakai git, scp, atau upload manual)
2. **Install Python, pip, venv di VM**
3. **Copy file credential ke VM** (jangan upload ke repo!)
4. **Set environment variable di shell VM**
   ```sh
   export GCS_BUCKET_NAME=your-bucket-name
   export GOOGLE_APPLICATION_CREDENTIALS=key.json
   export BASE_URL=http://<IP_VM>:8000
   ```
5. **Install requirements dan jalankan Gunicorn**
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   gunicorn --bind 127.0.0.1:8000 app:app
   ```
6. **Setup Nginx sebagai reverse proxy ke 127.0.0.1:8000**
7. **Akses API dari luar via Nginx (port 80)**

---

## Struktur File Penting
- `app.py` : Server Flask utama
- `gcs_handler.py` : Sinkronisasi dan upload ke GCS
- `test_client.py` : Client Python untuk testing
- `pepper_client.py` : Client untuk integrasi dengan robot Pepper
- `requirements.txt` : Daftar dependencies
- `key.json.example` : Contoh credential (isi dummy)
- `.gitignore` : Sudah mengabaikan file rahasia

---

## Catatan Keamanan
- **JANGAN pernah upload file credential asli ke repo public!**
- **Selalu gunakan environment variable untuk data sensitif.**
- **Update README jika ada variabel baru atau perubahan setup.**

---

Untuk pertanyaan lebih lanjut, silakan buka issue di repo ini atau hubungi maintainer. 

# Cara run Project Di Local Computer (Windows)

## 🧩 Prasyarat

### ✅ Install Python 3.10 (Windows)

1. Unduh dari [https://www.python.org/downloads/release/python-3100/](https://www.python.org/downloads/release/python-3100/)
2. Saat instalasi, **centang opsi "Add Python to PATH"**
3. Pilih “Customize installation”, lalu lanjutkan sampai selesai

Cek versi Python:

```powershell
py -3.10 --version
```

---

## 🚀 Cara Menjalankan Aplikasi (Lokal)

### 1. **Masuk ke folder aplikasi**

```powershell
cd "final test face reco app"
```

### 2. **Buat dan aktifkan virtual environment**

```powershell
py -3.10 -m venv env310
.\env310\Scripts\Activate.ps1
```

❗ Jika muncul error seperti:

```
cannot be loaded because running scripts is disabled...
```

Jalankan PowerShell sebagai administrator dan ketik:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

### 4. **Jalankan server**

```powershell
python app.py
```

Jika berhasil, server akan tersedia di:

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* atau IP lokal seperti [http://192.168.x.x:8000](http://192.168.x.x:8000)

---

## ⚙️ Penyesuaian Path Database Wajah (`LOCAL_DB_PATH`)

Secara default, lokasi penyimpanan database wajah diatur langsung di file `app.py` melalui variabel `LOCAL_DB_PATH`. Contoh:

```python
LOCAL_DB_PATH = r"C:\Users\GYAN\Documents\Magang\Sinergi Merah Putih\Robo Pepper\Face_Database"
```

Jika kamu menjalankan aplikasi di komputer lain, pastikan:

* **Folder path tersebut ada dan bisa ditulisi**
* Jika menggunakan folder lain, ubah nilai `LOCAL_DB_PATH` di `app.py` sesuai dengan lokasi folder wajah di komputermu

Contoh penggantian:

```python
# Ganti dengan folder yang sesuai di sistemmu
LOCAL_DB_PATH = r"C:\Users\<NAMAMU>\Documents\Face_Database"
```



