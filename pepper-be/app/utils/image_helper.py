from PIL import Image

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_MIME = ['image/jpeg', 'image/png']

def is_valid_image(file):
    filename = file.filename.lower()

    # 1. Cek ekstensi
    if '.' not in filename or filename.rsplit('.', 1)[1] not in ALLOWED_EXTENSIONS:
        return False, "Format file tidak didukung"

    # 2. Cek MIME type
    if file.mimetype not in ALLOWED_MIME:
        return False, "Tipe file tidak valid"

    # 3. Cek isi file pakai Pillow
    try:
        img = Image.open(file.stream)
        img.verify()  # Raise error kalau file bukan image valid
        file.stream.seek(0)  # Reset posisi pointer biar bisa dipakai ulang
        return True, None
    except Exception:
        return False, "File bukan gambar valid"
