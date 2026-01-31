import qi
import requests
import os
import time

# Ganti dengan IP VM Compute Engine kamu
BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

def main(session):
    tts = session.service("ALTextToSpeech")
    photo = session.service("ALPhotoCapture")

    # 1. Ambil foto
    tts.say("Saya akan mengambil foto untuk pengenalan wajah. Silakan menghadap kamera.")
    time.sleep(1)
    save_path = "/home/nao/recordings/cameras/"
    file_name = "face_capture.jpg"
    full_path = os.path.join(save_path, file_name)
    photo.setResolution(2)  # 640x480
    photo.takePicture(save_path, file_name)
    tts.say("Foto sudah diambil, saya akan mengirim ke server.")

    # 2. Kirim ke endpoint /recognize
    url = BASE_URL + "/recognize"
    try:
        with open(full_path, 'rb') as f:
            files = {'image': (file_name, f, 'image/jpeg')}
            response = requests.post(url, files=files, timeout=20)
            data = response.json()
            print("Respons dari server:", data)

            if data.get("status") == "recognized":
                nama = data.get("name")
                confidence = data.get("confidence", "N/A")
                tts.say("Hallo %s, selamat datang kembali. Kepercayaan saya %s." % (nama, confidence))
            elif data.get("status") == "unrecognized":
                tts.say(data.get("message", "Maaf, wajah anda tidak saya kenali."))
            else:
                tts.say("Terjadi kesalahan pada server.")
    except Exception as e:
        print("Error:", e)
        tts.say("Maaf, terjadi error saat mengirim ke server.")

# Untuk dijalankan di Choregraphe Python Script Box:
def onInput_onStart():
    try:
        app = qi.Application()
        app.start()
        main(app.session)
    except Exception as e:
        print("Error:", e)
    finally:
        onStopped()

def onStopped():
    pass