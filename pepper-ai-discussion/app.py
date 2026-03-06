#app.py
# 
# Copyright © 2025. All Rights Reserved.
# 
# PROPRIETARY AND CONFIDENTIAL
# This software is the proprietary information of the copyright holder.
# Unauthorized copying, distribution, or use is strictly prohibited.
# See LICENSE file in the root directory for terms and conditions.
#
import os
import base64
import json
from flask import Flask, request, jsonify
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from gtts import gTTS
import sounddevice as sd
import numpy as np
from google.cloud import speech
import requests
import tempfile
import wave
from google.cloud import texttospeech
import uuid
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Inisialisasi Vertex AI
#key_path = os.path.join(os.path.dirname(__file__), "key.json")
#os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

# Get project ID and location from environment variables for security
YOUR_PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT_ID", os.environ.get("GCP_PROJECT_ID"))
YOUR_VERTEX_AI_LOCATION = os.environ.get("VERTEX_AI_LOCATION", "us-central1")

if not YOUR_PROJECT_ID:
    raise ValueError("GOOGLE_CLOUD_PROJECT_ID or GCP_PROJECT_ID environment variable must be set")

vertexai.init(project=YOUR_PROJECT_ID, location=YOUR_VERTEX_AI_LOCATION)
model = GenerativeModel("gemini-2.0-flash")

# In-memory session store.
# WARNING: This is not suitable for production on Cloud Run with multiple
# instances, as each instance will have its own memory. Use a shared
# database like Redis or Firestore for session management in production.
SESSIONS = {}

DB_PATH = os.path.join(os.path.dirname(__file__), 'session_history.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def save_message(session_id, role, message):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO chat_history (session_id, role, message, timestamp) VALUES (?, ?, ?, ?)',
              (session_id, role, message, datetime.now()))
    conn.commit()
    conn.close()

def get_history(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT role, message FROM chat_history WHERE session_id = ? ORDER BY id ASC', (session_id,))
    rows = c.fetchall()
    conn.close()
    # Format sesuai dengan yang diharapkan VertexAI: [{'role': 'user', 'parts': [msg]}, ...]
    return [{'role': row[0], 'parts': [row[1]]} for row in rows]

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Voice Discussion</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            #micBtn {
                background: #f2f2f2;
                border: none;
                border-radius: 50%;
                width: 80px;
                height: 80px;
                font-size: 40px;
                cursor: pointer;
                box-shadow: 0 2px 8px #aaa;
                transition: background 0.2s;
                margin-top: 40px;
            }
            #micBtn.recording {
                background: #ff5252;
                color: #fff;
            }
            #response { margin-top: 40px; }
            #log { color: #888; font-size: 12px; margin-top: 20px; }
        </style>
    </head>
    <body>
        <h1>AI Voice Discussion</h1>
        <button id="micBtn" title="Tap to record"><span id="micIcon">🎤</span></button>
        <div id="response"></div>
        <div id="log"></div>
        <script>
        let mediaRecorder;
        let audioChunks = [];
        let isRecording = false;
        const micBtn = document.getElementById('micBtn');
        const micIcon = document.getElementById('micIcon');
        const responseDiv = document.getElementById('response');
        const logDiv = document.getElementById('log');

        function log(msg) {
            console.log('[AI DISCUSSION]', msg);
            logDiv.innerHTML += msg + '<br>';
        }

        async function startRecording() {
            log('Start recording...');
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert('Browser tidak mendukung perekaman audio.');
                log('getUserMedia not supported');
                return;
            }
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                log('Microphone access granted');
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0) audioChunks.push(event.data);
                    log('Data available, size: ' + event.data.size);
                };
                mediaRecorder.onstop = async () => {
                    log('Recording stopped');
                    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                    log('Audio blob created, size: ' + audioBlob.size);
                    const reader = new FileReader();
                    reader.readAsDataURL(audioBlob);
                    reader.onloadend = async () => {
                        const base64Audio = reader.result.split(',')[1];
                        log('Audio converted to base64, length: ' + base64Audio.length);
                        responseDiv.innerHTML = '<p>Processing...</p>';
                        try {
                            log('Sending audio to backend...');
                            const response = await fetch('/api/process-audio', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ audio: base64Audio })
                            });
                            log('Response received from backend');
                            const result = await response.json();
                            log('Response JSON: ' + JSON.stringify(result));
                            if (result.answer && result.audio_base64) {
                                responseDiv.innerHTML =
                                    `<p><b>Pertanyaan:</b> ${result.question}</p>` +
                                    `<p><b>Jawaban:</b> ${result.answer}</p>` +
                                    `<audio controls src="data:audio/mp3;base64,${result.audio_base64}"></audio>`;
                                log('Answer and audio displayed');
                            } else {
                                responseDiv.innerHTML = `<p style='color:red;'>${result.error || 'Terjadi kesalahan.'}</p>`;
                                log('Error from backend: ' + (result.error || 'Unknown error'));
                            }
                        } catch (err) {
                            responseDiv.innerHTML = `<p style='color:red;'>Gagal mengirim audio: ${err}</p>`;
                            log('Fetch error: ' + err);
                        }
                    };
                };
                mediaRecorder.start();
                isRecording = true;
                micBtn.classList.add('recording');
                micIcon.textContent = '⏹️';
                log('MediaRecorder started');
            } catch (err) {
                alert('Tidak bisa mengakses mikrofon: ' + err);
                log('Microphone access error: ' + err);
            }
        }

        function stopRecording() {
            if (mediaRecorder && isRecording) {
                mediaRecorder.stop();
                isRecording = false;
                micBtn.classList.remove('recording');
                micIcon.textContent = '🎤';
                log('Stop recording requested');
            }
        }

        micBtn.onclick = () => {
            if (!isRecording) {
                startRecording();
            } else {
                stopRecording();
            }
        };
        </script>
    </body>
    </html>
    '''

# Endpoint untuk menerima audio dari robot
from pydub import AudioSegment

@app.route('/api/process-audio', methods=['POST'])
def api_process_audio():
    try:
        print('[API] Request received')
        if not request.is_json:
            return jsonify({'error': 'Content-Type harus application/json'}), 400

        data = request.get_json()
        audio_data = data.get('audio')
        session_id = data.get('session_id')

        if not audio_data:
            return jsonify({'error': 'Audio data tidak ditemukan'}), 400

        if not session_id:
            session_id = uuid.uuid4().hex
            print(f'[API] New session created: {session_id}')

        # Ambil history dari database
        history = get_history(session_id)
        chat = model.start_chat(history=history)

        # Simpan file sementara
        audio_bytes = base64.b64decode(audio_data)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_input:
            temp_input.write(audio_bytes)
            input_path = temp_input.name

        # Konversi ke WAV 16kHz mono dengan pydub
        sound = AudioSegment.from_file(input_path)
        sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        temp_converted = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        sound.export(temp_converted.name, format="wav")
        converted_path = temp_converted.name
        print('[API] Audio converted to 16kHz mono WAV')
        with open(converted_path, 'rb') as f:
            converted_bytes = f.read()

        # Kirim ke Google STT
        speech_client = speech.SpeechClient()
        audio = speech.RecognitionAudio(content=converted_bytes)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="id-ID",
            enable_automatic_punctuation=True
        )
        print('[API] Sending to Google STT...')
        response = speech_client.recognize(config=config, audio=audio)

        question = ""
        for result in response.results:
            question += result.alternatives[0].transcript
        print('[API] STT result:', question)
        if not question:
            return jsonify({'error': 'Tidak ada teks yang terdeteksi', 'session_id': session_id}), 400

        # Simpan pertanyaan user ke DB
        save_message(session_id, 'user', question)

        # Gemini
        print(f'[API] Sending message to Gemini for session {session_id}. History length: {len(history)}')
        prompt = (
            u"Jawab pertanyaan berikut secara singkat, jelas, dan tidak lebih dari 3 kalimat. "
            u"Jangan mengulang pertanyaan. "
            u"Pertanyaan: %s" % question
        )
        gemini_response = chat.send_message(prompt)
        answer = gemini_response.text
        print('[API] Gemini answer:', answer)

        # Simpan jawaban ke DB
        save_message(session_id, 'assistant', answer)

        # TTS
        synthesize_speech(answer, "temp_response.mp3")
        with open("temp_response.mp3", "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')
        os.remove("temp_response.mp3")

        return jsonify({
            'question': question,
            'answer': answer,
            'audio_base64': audio_base64,
            'session_id': session_id
        })

    except Exception as e:
        print('[API] ERROR:', str(e))
        return jsonify({'error': str(e)}), 500

# Endpoint untuk testing API
@app.route('/api/test', methods=['POST'])
def test_api():
    try:
        test_text = "Halo, ini adalah tes API."
        # Generate response dari Gemini
        gemini_response = model.generate_content(test_text)
        answer = gemini_response.text

        # Convert ke audio
        synthesize_speech(answer, "temp_test_response.mp3")

        with open("temp_test_response.mp3", "rb") as audio_file:
            audio_base64 = base64.b64encode(audio_file.read()).decode('utf-8')

        os.remove("temp_test_response.mp3")

        return jsonify({
            'status': 'success',
            'data': {
                'test_text': test_text,
                'answer': answer,
                'audio': audio_base64
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

# Fungsi untuk merekam audio dari mic (format: WAV)
def record_audio(duration=5, fs=16000):
    print(f"Rekam suara selama {duration} detik...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
    sd.wait()
    return audio, fs

# Simpan audio ke file WAV sementara
def save_wav(audio, fs):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    with wave.open(temp.name, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(fs)
        wf.writeframes(audio.tobytes())
    return temp.name

# Konversi file audio ke base64
def audio_to_base64(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Kirim audio ke server dan terima jawaban
def send_audio_to_server(audio_base64, server_url):
    payload = {'audio': audio_base64}
    r = requests.post(server_url, json=payload)
    r.raise_for_status()
    return r.json()

# Main loop
def main():
    SERVER_URL = 'http://localhost:5000/api/process-audio'  # Ganti jika server beda
    while True:
        input("Tekan ENTER untuk mulai rekam (atau Ctrl+C untuk keluar)...")
        audio, fs = record_audio(duration=5)
        wav_path = save_wav(audio, fs)
        audio_b64 = audio_to_base64(wav_path)
        print("Mengirim audio ke server...")
        try:
            response = send_audio_to_server(audio_b64, SERVER_URL)
            print("Jawaban dari AI:", response.get('answer'))
            # Jika ingin Pepper mengucapkan:
            # pepper_say(response.get('answer'))
            # Jika ingin play audio TTS:
            if response.get('audio_base64'):
                tts_path = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
                with open(tts_path, 'wb') as f:
                    f.write(base64.b64decode(response['audio_base64']))
                print(f"Audio jawaban disimpan di: {tts_path}")
                # Play audio jika ingin (gunakan mpg123/vlc atau library lain)
        except Exception as e:
            print("Gagal:", e)

def synthesize_speech(text, output_path):
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    # Pilih voice yang natural
    voice = texttospeech.VoiceSelectionParams(
        language_code="id-ID",
        name="id-ID-Wavenet-A",  # Coba juga id-ID-Wavenet-B, dst
        ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0
    )
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    with open(output_path, "wb") as out:
        out.write(response.audio_content)

if __name__ == '__main__':
    if os.environ.get("RUN_LOCAL", "false").lower() == "true":
        main()  # jalankan hanya saat lokal
    else:
        app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

