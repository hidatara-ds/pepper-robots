import requests
import base64
import os

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8000")

def test_recognize(image_path):
    """
    Mengirim gambar ke endpoint /recognize untuk dikenali.
    """
    if not os.path.exists(image_path):
        print(f"Error: File gambar tidak ditemukan di {image_path}")
        return

    print(f"\n--- MENCOBA MENGENALI WAJAH DARI: {image_path} ---")
    url = f"{BASE_URL}/recognize"
    
    with open(image_path, 'rb') as f:
        files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
        try:
            response = requests.post(url, files=files)
            response.raise_for_status()  # Akan error jika status code bukan 2xx
            
            data = response.json()
            print("Respons dari server (JSON):", data)

            if data.get("status") == "recognized":
                nama = data.get("name")
                confidence = data.get("confidence", "N/A") # Ambil skor confidence
                print(f"\n>>> Output Aplikasi: Hallo {nama}, selamat datang kembali (Kepercayaan: {confidence})")
            elif data.get("status") == "unrecognized":
                print(f"\n>>> Output Aplikasi: {data.get('message')}")
            else: # Menangani kemungkinan status error dari server
                print(f"\n>>> Output Aplikasi: Terjadi kesalahan: {data.get('message')}")

        except requests.exceptions.RequestException as e:
            print(f"Error saat request: {e}")


def test_register(person_name, image_path):
    """
    Mendaftarkan wajah baru ke endpoint /register.
    """
    if not os.path.exists(image_path):
        print(f"Error: File gambar tidak ditemukan di {image_path}")
        return

    print(f"\n--- MENDAFTARKAN WAJAH BARU: {person_name} DARI {image_path} ---")
    url = f"{BASE_URL}/register"

    # Baca gambar dan encode ke base64
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')

    payload = {
        "name": person_name,
        "image": encoded_string
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Respons dari server:")
        print(response.json())
    except requests.exceptions.RequestException as e:
        print(f"Error saat request: {e}")


if __name__ == '__main__':
    # --- SIAPKAN GAMBAR UNTUK TES ---
    # Ganti 'path/to/your/image.jpg' dengan path gambar yang ada di komputermu
    # Misalnya, kamu bisa pakai gambar yang sudah ada di folder `gcs_database`
    
    # Contoh 1: Mengenali wajah yang sudah ada di database (misal: ronaldo.jpg)
    # Pastikan file ini ada setelah sinkronisasi GCS
    image_to_recognize = r'your path image'
    if os.path.exists(image_to_recognize):
        test_recognize(image_to_recognize)
    else:
        print(f"Peringatan: File {image_to_recognize} tidak ditemukan. Tes pengenalan dilewati.")
        print("Pastikan nama file dan path-nya benar.")

    # Contoh 2: Mendaftarkan wajah baru
    # Ganti 'NAMA_BARU' dan path ke gambar barumu
    # new_person_name = "NAMA_BARU"
    # image_for_register = "path/ke/gambar/baru.jpg"
    # if os.path.exists(image_for_register):
    #     test_register(new_person_name, image_for_register)
    #
    #     # Setelah mendaftar, coba kenali wajah yang baru didaftarkan
    #     print("\nMenunggu beberapa detik agar server sinkronisasi...")
    #     import time
    #     time.sleep(5) # Beri waktu server untuk sinkronisasi
    #     test_recognize(image_for_register)
    # else:
    #     print("\nLewati tes pendaftaran karena file gambar tidak ditemukan.")

    print("\n--- Tes Selesai ---") 