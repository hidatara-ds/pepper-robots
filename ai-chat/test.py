import base64
import requests
from pydub import AudioSegment
import tempfile
import os

# === SETTING ===
INPUT_PATH = r"C:\Users\deyay\Documents\Sound Recordings\test.wav"
API_URL = "https://be-pepper-rumpi-340228211998.asia-southeast2.run.app/api/process-audio"

# === STEP 1: Konversi ke WAV 16kHz mono ===
sound = AudioSegment.from_file(INPUT_PATH)
sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)

with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_wav:
    converted_path = temp_wav.name
    sound.export(converted_path, format="wav")

# === STEP 2: Encode WAV ke base64 ===
with open(converted_path, "rb") as f:
    audio_base64 = base64.b64encode(f.read()).decode("utf-8")

# === STEP 3: Kirim ke API ===
payload = {
    "audio": audio_base64
}

headers = {
    "Content-Type": "application/json"
}

try:
    response = requests.post(API_URL, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    print("== RESPONSE ==")
    print("Pertanyaan:", result.get("question"))
    print("Jawaban:", result.get("answer"))

    # Simpan file MP3 kalau ada audio
    if result.get("audio_base64"):
        out_path = "response_audio.mp3"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(result["audio_base64"]))
        print(f"Audio TTS disimpan di: {out_path}")

except requests.exceptions.RequestException as e:
    print("ERROR saat request:", e)
finally:
    os.remove(converted_path)
