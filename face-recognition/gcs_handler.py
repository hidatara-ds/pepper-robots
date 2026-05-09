# gcs_handler.py
# 
# Copyright © 2025. All Rights Reserved.
# 
# PROPRIETARY AND CONFIDENTIAL
# This software is the proprietary information of the copyright holder.
# Unauthorized copying, distribution, or use is strictly prohibited.
# See LICENSE file in the root directory for terms and conditions.
#
import os

GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "face-recognition-db")
GOOGLE_APPLICATION_CREDENTIALS = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "key.json")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS
from google.cloud import storage
from google.api_core.exceptions import NotFound

# Konfigurasi GCS
# Ganti dengan nama bucket GCS Anda
# Direktori lokal untuk menyimpan database wajah yang disinkronkan
LOCAL_DB_PATH = "gcs_database" 

def synchronize_gcs_to_local():
    """
    Melakukan sinkronisasi cerdas antara GCS dan direktori lokal.
    - Mengunduh file baru dari GCS.
    - Menghapus file lokal yang tidak ada lagi di GCS.
    - Menghapus cache DeepFace (.pkl) hanya jika ada perubahan.
    """
    print("Memulai sinkronisasi cerdas...")
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
    except Exception as e:
        print(f"Error: Gagal menginisialisasi klien GCS. Detail: {e}")
        return

    # 1. Dapatkan daftar file (path relatif) dari GCS
    gcs_files = {blob.name for blob in bucket.list_blobs()}

    # 2. Dapatkan daftar file (path relatif) dari direktori lokal
    if not os.path.exists(LOCAL_DB_PATH):
        os.makedirs(LOCAL_DB_PATH)
    
    local_files = set()
    for root, _, files in os.walk(LOCAL_DB_PATH):
        for name in files:
            if name.endswith(".pkl"):  # Abaikan file cache DeepFace
                continue
            local_path = os.path.join(root, name)
            # Buat path relatif untuk perbandingan, pastikan separatornya '/'
            relative_path = os.path.relpath(local_path, LOCAL_DB_PATH).replace('\\', '/')
            local_files.add(relative_path)

    # 3. Tentukan file yang akan diunduh dan dihapus
    files_to_download = gcs_files - local_files
    files_to_delete = local_files - gcs_files

    db_changed = False

    # 4. Unduh file-file baru
    if files_to_download:
        db_changed = True
        print(f"Ditemukan {len(files_to_download)} file baru untuk diunduh.")
        for file_path in files_to_download:
            # Lewati "objek" folder yang ditandai dengan '/' di akhir nama
            if file_path.endswith('/'):
                print(f"Melewati objek folder: {file_path}")
                continue
                
            blob = bucket.blob(file_path)
            # Ganti separator agar sesuai dengan sistem operasi lokal
            destination_file_path = os.path.join(LOCAL_DB_PATH, file_path.replace('/', os.sep))
            
            # Buat direktori jika belum ada
            destination_dir = os.path.dirname(destination_file_path)
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            
            print(f"Mengunduh {file_path}...")
            blob.download_to_filename(destination_file_path)

    # 5. Hapus file-file lama
    if files_to_delete:
        db_changed = True
        print(f"Ditemukan {len(files_to_delete)} file lama untuk dihapus.")
        for file_path in files_to_delete:
            local_file_to_delete = os.path.join(LOCAL_DB_PATH, file_path.replace('/', os.sep))
            if os.path.exists(local_file_to_delete):
                print(f"Menghapus {local_file_to_delete}...")
                os.remove(local_file_to_delete)

    # 6. Hapus file cache .pkl jika database berubah
    if db_changed:
        print("Database berubah. Menghapus file cache representasi DeepFace.")
        pkl_file = os.path.join(LOCAL_DB_PATH, "representations_vgg_face.pkl")
        if os.path.exists(pkl_file):
            os.remove(pkl_file)
    else:
        print("Database lokal sudah sinkron dengan GCS.")
    
    print("Sinkronisasi cerdas selesai.")


def upload_face_to_gcs(image_path, person_name):
    """
    Mengunggah file gambar ke GCS di bawah folder nama orang tersebut.
    
    Args:
        image_path (str): Jalur ke file gambar lokal yang akan diunggah.
        person_name (str): Nama orang, digunakan sebagai nama folder di GCS.

    Returns:
        tuple: (bool, dict) - (status berhasil, dict berisi url dan blob_name jika berhasil, None jika gagal).
    """
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        
        # Tentukan nama file unik untuk menghindari tumpang tindih
        file_name = os.path.basename(image_path)
        destination_blob_name = f"faces/{person_name}/{file_name}"
        
        blob = bucket.blob(destination_blob_name)
        
        print(f"Mengunggah {image_path} ke GCS di gs://{GCS_BUCKET_NAME}/{destination_blob_name}")
        blob.upload_from_filename(image_path)
        
        # Generate the public URL with correct format
        gcs_url = f"https://storage.googleapis.com/{GCS_BUCKET_NAME}/faces/{person_name}/{file_name}"
        
        print(f"Unggahan berhasil. URL: {gcs_url}")
        # Kembalikan juga blob_name
        return True, {
            "gcs_url": gcs_url,
            "blob_name": destination_blob_name
        }
    except Exception as e:
        print(f"Error: Gagal mengunggah file ke GCS. Detail: {e}")
        return False, None