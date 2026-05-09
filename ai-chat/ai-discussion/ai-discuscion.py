import base64
import json
import requests
import os
import time

try:
    from naoqi import ALProxy
    TTS = ALProxy("ALTextToSpeech", "127.0.0.1", 9559)
    Recorder = ALProxy("ALAudioRecorder", "127.0.0.1", 9559)
    AudioPlayer = ALProxy("ALAudioPlayer", "127.0.0.1", 9559)
    AudioDevice = ALProxy("ALAudioDevice", "127.0.0.1", 9559)  # Tambahan untuk atur volume

    def speak(text):
        try:
            TTS.say(text)
        except Exception:
            pass
except Exception:
    Recorder = None
    AudioPlayer = None
    AudioDevice = None

    def speak(text):
        pass  # fallback jika tidak di robot

api_url = "https://be-pepper-rumpi-340228211998.asia-southeast2.run.app/api/process-audio"

def main():
    # 1. Mulai rekam suara
    timestamp = int(time.time())
    tmp_wav = "/tmp/rec_{}.wav".format(timestamp)
    channels = [1, 1, 1, 1]  # [Left, Right, Front, Rear] (1=aktif, 0=tidak)
    sample_rate = 16000

    print("[INFO] Mulai merekam suara...")
    speak("Mulai merekam suara")
    if Recorder:
        try:
            Recorder.startMicrophonesRecording(tmp_wav, "wav", sample_rate, channels)
            time.sleep(5)  # Rekam selama 5 detik
            Recorder.stopMicrophonesRecording()
            print("[SUCCESS] Rekaman selesai, file disimpan di:", tmp_wav)
            speak("Rekaman selesai")
        except Exception as e:
            print("[ERROR] Gagal merekam:", e)
            speak("Gagal merekam suara")
            return
    else:
        print("[ERROR] Tidak bisa akses ALAudioRecorder")
        speak("Tidak bisa akses mikrofon")
        return

    # 2. Encode dan kirim ke server
    if not os.path.exists(tmp_wav):
        print("[ERROR] File rekaman tidak ditemukan:", tmp_wav)
        speak("File rekaman tidak ditemukan")
        return

    try:
        with open(tmp_wav, "rb") as audio_file:
            audio_bytes = audio_file.read()
            print("[SUCCESS] File audio berhasil dibaca ({} bytes)".format(len(audio_bytes)))
            audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")
            print("[SUCCESS] File audio berhasil di-encode ke base64 (panjang string: {})".format(len(audio_base64)))
    except Exception as e:
        print("[ERROR] Gagal membaca/encode file audio:", e)
        speak("Gagal membaca file audio")
        os.remove(tmp_wav)
        return

    payload = {
        "audio": audio_base64
    }
    headers = {
        "Content-Type": "application/json"
    }
    print("[INFO] Payload dan headers siap, mulai mengirim request ke server...")
    speak("Mengirim ke server")

    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        print("[SUCCESS] Request berhasil dikirim. Status code:", response.status_code)
    except Exception as e:
        print("[ERROR] Gagal request ke server:", e)
        speak("Gagal mengirim ke server")
        os.remove(tmp_wav)
        return

    if response.status_code != 200:
        print("[ERROR] Status code bukan 200:", response.status_code)
        print("[INFO] Response text:", response.text)
        speak("Server error")
        os.remove(tmp_wav)
        return

    try:
        result = response.json()
        print("[SUCCESS] Response diterima dalam bentuk JSON:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print("[ERROR] Gagal decode response JSON:", e)
        print("[INFO] Response text:", response.text)
        speak("Jawaban server tidak bisa dibaca")
        os.remove(tmp_wav)
        return

    # 3. Play audio dari server, atau fallback ke TTS
    if result.get("audio_base64"):
        out_path = "/tmp/response_audio_{}.mp3".format(timestamp)
        try:
            with open(out_path, "wb") as f:
                f.write(base64.b64decode(result["audio_base64"]))
            print("[SUCCESS] Audio TTS disimpan di:", out_path)

            if AudioPlayer:
                try:
                    print("[INFO] Mengatur volume ke maksimum (100)...")
                    AudioDevice.setOutputVolume(100)
                except Exception as e:
                    print("[WARNING] Gagal mengatur volume:", e)

                print("[INFO] Memutar audio jawaban dari server...")
                speak("Memutar jawaban dari server")
                AudioPlayer.playFile(out_path)
            else:
                print("[ERROR] Tidak bisa akses ALAudioPlayer, fallback ke TTS")
                if result.get("answer"):
                    speak(result["answer"])
        except Exception as e:
            print("[ERROR] Gagal menyimpan/memutar audio TTS:", e)
            speak("Gagal memutar audio jawaban, saya akan membacakannya")
            if result.get("answer"):
                speak(result["answer"])
    elif result.get("answer"):
        print("[INFO] Tidak ada audio_base64, membacakan jawaban dengan TTS Pepper")
        speak(result["answer"])
    else:
        print("[ERROR] Tidak ada jawaban di response")
        speak("Maaf, saya tidak mengerti")

    print("[INFO] Script selesai.")
    speak("Selesai")

    # Hapus file rekaman agar tidak penuhi memory
    try:
        os.remove(tmp_wav)
        print("[INFO] File rekaman dihapus dari tmp.")
    except Exception:
        pass

if __name__ == "__main__":
    main()
