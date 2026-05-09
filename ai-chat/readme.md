# Pepper AI Voice Discussion API

A Flask-based REST API for AI voice discussions. This API accepts audio (base64), converts it to text (Google Speech-to-Text), processes questions through Gemini (Vertex AI), then converts answers to natural voice (Google Cloud Text-to-Speech/WaveNet). Responses are returned in JSON format (text & audio base64).

**Copyright Notice**: This software is proprietary research work. All rights reserved by the original creator. See LICENSE file in the root directory for usage terms.

---

## Features
- Record voice via web (mic) or Python client
- Speech-to-Text (Google Cloud STT)
- Prompt to Gemini (Vertex AI)
- Text-to-Speech (Google Cloud TTS, natural voice)
- Response: JSON `{question, answer, audio_base64}`
- Ready to deploy to Cloud Run

---

## Local Setup

### 1. Clone Repo & Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Google Cloud Credentials
- Enable APIs: Speech-to-Text, Text-to-Speech, Vertex AI in Google Cloud Console
- Download service account key (JSON), save as `key.json` in project folder

### 3. Run App
```bash
python app.py
```

Access web UI at: [http://localhost:5000](http://localhost:5000)

---

## Deploy to Cloud Run via GitHub
1. Push all files to GitHub repo
2. Create `Dockerfile` like this:
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT=8080
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app
```
3. Connect repo to Cloud Run (Deploy from source)
4. Add secret/key.json to Secret Manager, mount to container
5. Set env var `GOOGLE_APPLICATION_CREDENTIALS` to key.json path

---

## API Request Example

### POST /api/process-audio
```bash
curl -X POST https://<YOUR_CLOUD_RUN_URL>/api/process-audio \
  -H "Content-Type: application/json" \
  -d '{"audio": "<base64-audio>"}'
```
**Response:**
```json
{
  "question": "How are you?",
  "answer": "I'm doing well, thank you!",
  "audio_base64": "..."
}
```

---

## Python Client (Example)
See the `main()` function in `app.py` for example client script that records voice, sends to API, and receives answers.

---

## Customization
- Change Google TTS voice in `synthesize_speech()` function (see [voice list](https://cloud.google.com/text-to-speech/docs/voices)).
- Gemini prompt can be modified in `/api/process-audio` endpoint.

---

## 📄 License

This software is proprietary and protected by copyright law. See the LICENSE file in the root directory for complete terms and conditions.

**Copyright © 2025. All Rights Reserved.**

---

## 🙏 Citation

If you reference this work in academic papers or research, please cite appropriately. This project represents significant original research effort in AI-powered voice interaction systems.
