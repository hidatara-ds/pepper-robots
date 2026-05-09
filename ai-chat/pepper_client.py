# -*- coding: utf-8 -*-
import sys
import os
import time
import base64
import json
import requests

from naoqi import ALProxy

try:
    MEMORY = ALProxy("ALMemory", "127.0.0.1", 9559)
    TTS = ALProxy("ALTextToSpeech", "127.0.0.1", 9559)
    Recorder = ALProxy("ALAudioRecorder", "127.0.0.1", 9559)
    AudioPlayer = ALProxy("ALAudioPlayer", "127.0.0.1", 9559)
except Exception as e:
    print "[ERROR] Tidak bisa inisialisasi NAOqi Proxy:", str(e)
    sys.exit(1)

# Get API URL from environment variable for security
api_url = os.environ.get("AI_DISCUSSION_API_URL", "http://localhost:5000/api/process-audio")
channels = [1, 1, 1, 1]
sample_rate = 16000

def speak(text):
    try:
        TTS.say(text)
    except:
        pass

def start_recognitionrding():
    timestamp = int(time.time())
    filepath = "/tmp/rec_{}.wav".format(timestamp)
    MEMORY.insertData("pepper_recognitionrding_path", filepath)
    MEMORY.insertData("pepper_is_recognitionrding", True)

    try:
        Recorder.startMicrophonesRecording(filepath, "wav", sample_rate, channels)
        speak("Mulai merekam")
        print "[INFO] Mulai merekam ke: {}".format(filepath)
    except Exception as e:
        print "[ERROR] Gagal mulai rekaman:", str(e)
        speak("Gagal mulai merekam")

def stop_and_process():
    try:
        is_recognitionrding = MEMORY.getData("pepper_is_recognitionrding")
    except:
        print "[ERROR] Tidak ada status rekaman"
        speak("Tidak ada rekaman yang sedang berjalan")
        return

    if not is_recognitionrding:
        print "[INFO] Tidak sedang merekam"
        speak("Belum ada rekaman")
        return

    filepath = MEMORY.getData("pepper_recognitionrding_path")
    try:
        Recorder.stopMicrophonesRecording()
        print "[INFO] Rekaman dihentikan:", filepath
        speak("Rekaman selesai")
    except Exception as e:
        print "[ERROR] Gagal stop rekaman:", str(e)
        speak("Gagal menghentikan rekaman")
        return

    if not os.path.exists(filepath):
        print "[ERROR] File tidak ditemukan:", filepath
        speak("File rekaman tidak ditemukan")
        return

    # Kirim ke AI
    try:
        with open(filepath, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        print "[ERROR] Gagal baca file audio:", str(e)
        speak("Gagal membaca file audio")
        return

    payload = { "audio": audio_b64 }
    headers = { "Content-Type": "application/json" }

    try:
        # SSL verification should be enabled in production for security
        # Set REQUESTS_CA_BUNDLE or SSL_CERT_FILE env var if using custom certificates
        response = requests.post(api_url, json=payload, headers=headers, timeout=30, verify=True)
    except Exception as e:
        print "[ERROR] Gagal kirim request:", str(e)
        speak("Gagal mengirim ke server")
        return

    if response.status_code != 200:
        print "[ERROR] Server balas kode:", response.status_code
        speak("Server error")
        return

    try:
        result = response.json()
    except Exception as e:
        print "[ERROR] Gagal parse JSON:", str(e)
        speak("Gagal membaca balasan")
        return

    # Putar audio balasan
    if result.get("audio_base64"):
        out_path = "/tmp/response_{}.mp3".format(int(time.time()))
        try:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(result["audio_base64"]))
            print "[INFO] Audio jawaban disimpan:", out_path
            AudioPlayer.playFile(out_path)
        except Exception as e:
            print "[ERROR] Gagal putar audio:", str(e)
            if result.get("answer"):
                speak(result["answer"])
    elif result.get("answer"):
        speak(result["answer"])
    else:
        speak("Maaf, tidak ada jawaban")

    # Cleanup
    try:
        os.remove(filepath)
        MEMORY.removeData("pepper_recognitionrding_path")
        MEMORY.removeData("pepper_is_recognitionrding")
        print "[INFO] Cleanup selesai"
    except:
        pass

def main():
    if len(sys.argv) < 2:
        print "Usage: python audio_handler.py [start|stop]"
        return

    cmd = sys.argv[1]
    if cmd == "start":
        start_recognitionrding()
    elif cmd == "stop":
        stop_and_process()
    else:
        print "Perintah tidak dikenali:", cmd

if __name__ == "__main__":
    main()
