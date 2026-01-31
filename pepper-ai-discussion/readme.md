# Pepper Rumpi - AI Voice Discussion API

Pepper Rumpi adalah REST API berbasis Flask untuk diskusi suara AI. API ini menerima audio (base64), mengubahnya menjadi teks (Google Speech-to-Text), memproses pertanyaan ke Gemini (Vertex AI), lalu mengubah jawaban ke suara natural (Google Cloud Text-to-Speech/WaveNet). Jawaban dikembalikan dalam format JSON (teks & audio base64).

---

## Fitur
- Rekam suara via web (mic) atau client Python
- Speech-to-Text (Google Cloud STT)
- Prompt ke Gemini (Vertex AI)
- Text-to-Speech (Google Cloud TTS, suara natural)
- Response: JSON `{question, answer, audio_base64}`
- Siap di-deploy ke Cloud Run

---

## Setup Lokal

### 1. Clone Repo & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Siapkan Google Cloud Credential
- Aktifkan API: Speech-to-Text, Text-to-Speech, Vertex AI di Google Cloud Console
- Download service account key (JSON), simpan sebagai `key.json` di folder project

### 3. Jalankan App
```bash
python app.py
```

Akses web UI di: [http://localhost:5000](http://localhost:5000)

---

## Deploy ke Cloud Run via GitHub
1. Push semua file ke repo GitHub
2. Buat `Dockerfile` seperti berikut:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
```
3. Hubungkan repo ke Cloud Run (Deploy from source)
4. Tambahkan secret/key.json ke Secret Manager, mount ke container
5. Set env var `GOOGLE_APPLICATION_CREDENTIALS` ke path key.json

---

## Contoh Request API

### POST /api/process-audio
```bash
curl -X POST https://<YOUR_CLOUD_RUN_URL>/api/process-audio \
  -H "Content-Type: application/json" \
  -d '{"audio": "<base64-audio>"}'
```
**Response:**
```json
{
  "question": "Apa kabar?",
  "answer": "Saya baik, terima kasih!",
  "audio_base64": "..."
}
```

---

## Client Python (Contoh)
Lihat fungsi `main()` di `app.py` untuk contoh script client yang merekam suara, mengirim ke API, dan menerima jawaban.

---

## Customisasi
- Ganti voice Google TTS di fungsi `synthesize_speech()` (lihat [daftar voice](https://cloud.google.com/text-to-speech/docs/voices)).
- Prompt Gemini bisa diubah di endpoint `/api/process-audio`.

---

## Lisensi
MIT
