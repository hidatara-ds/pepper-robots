# Face Recognition API with Flask and Google Cloud Storage

A Flask-based REST API for face recognition and registration, utilizing DeepFace and Google Cloud Storage (GCS) as the face image database.

> **Note**: This project was originally developed as part of an Apple Developer Academy application portfolio and represents significant personal effort. While it's open source under MIT License, please provide proper attribution when using this code.

## Features
- Automatic face database synchronization from GCS
- `/recognize` endpoint for face recognition
- `/validate_face_image` endpoint to detect if a face is present in an image
- `/register` endpoint for registering new faces
- Python client support (can be integrated with Pepper robot)

---

## Prerequisites
- **Python 3.10**
- **Google Cloud Service Account** and credential file (see below)
- **GCS Bucket** for face image database

---

## Secure Setup for Public Repository

### 1. **DO NOT upload `key.json` file to the repository!**
- The `key.json` file is already in `.gitignore`.
- Only upload `key.json.example` (with dummy content, not real credentials).

### 2. **All sensitive variables are configured via environment variables**
- Bucket name, credential path, and BASE_URL are **not hardcoded** in the code.
- All Python scripts retrieve the following variables from environment:
  - `GCS_BUCKET_NAME` (GCS bucket name)
  - `GOOGLE_APPLICATION_CREDENTIALS` (path to credential file, default: `key.json`)
  - `BASE_URL` (API server address, default: `http://localhost:8000`)

### 3. **Example credential file**
- File `key.json.example` is provided. Copy it to `key.json` and fill with your actual credentials.

---

## Local Development Setup

1. **Clone repository and navigate to project folder**
2. **Copy credential file**
   ```sh
   cp key.json.example key.json
   # Then edit and fill with actual credentials
   ```
3. **Set environment variables** (Linux/macOS)
   ```sh
   export GCS_BUCKET_NAME=your-bucket-name
   export GOOGLE_APPLICATION_CREDENTIALS=key.json
   export BASE_URL=http://localhost:8000
   ```
   (Windows: use `set` or `.env` depending on your shell)
4. **Create and activate virtual environment**
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
5. **Run server**
   ```sh
   python app.py
   # or for production:
   gunicorn --bind 127.0.0.1:8000 app:app
   ```
6. **Run client/test**
   - Edit `BASE_URL` in environment variable if needed.
   - Run `test_client.py` or integrate with Pepper robot using `pepper_client.py`.

---

## Deploy to Compute Engine (Cloud)

1. **Copy project to VM** (using git, scp, or manual upload)
2. **Install Python, pip, venv on VM**
3. **Copy credential file to VM** (don't upload to repository!)
4. **Set environment variables in VM shell**
   ```sh
   export GCS_BUCKET_NAME=your-bucket-name
   export GOOGLE_APPLICATION_CREDENTIALS=key.json
   export BASE_URL=http://<VM_IP>:8000
   ```
5. **Install requirements and run Gunicorn**
   ```sh
   python3.10 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   gunicorn --bind 127.0.0.1:8000 app:app
   ```
6. **Setup Nginx as reverse proxy to 127.0.0.1:8000**
7. **Access API from outside via Nginx (port 80)**

---

## Important File Structure
- `app.py` : Main Flask server
- `gcs_handler.py` : GCS synchronization and upload
- `test_client.py` : Python client for testing
- `pepper_client.py` : Client for Pepper robot integration
- `requirements.txt` : Dependencies list
- `key.json.example` : Credential example (dummy content)
- `.gitignore` : Already ignoring sensitive files

---

## Security Notes
- **NEVER upload actual credential files to public repository!**
- **Always use environment variables for sensitive data.**
- **Update README if there are new variables or setup changes.**

---

# Running Project on Local Computer (Windows)

## 🧩 Prerequisites

### ✅ Install Python 3.10 (Windows)

1. Download from [https://www.python.org/downloads/release/python-3100/](https://www.python.org/downloads/release/python-3100/)
2. During installation, **check the "Add Python to PATH" option**
3. Select "Customize installation", then continue until complete

Check Python version:

```powershell
py -3.10 --version
```

---

## 🚀 Running the Application (Local)

### 1. **Navigate to application folder**

```powershell
cd "final test face reco app"
```

### 2. **Create and activate virtual environment**

```powershell
py -3.10 -m venv env310
.\env310\Scripts\Activate.ps1
```

❗ If you encounter an error like:

```
cannot be loaded because running scripts is disabled...
```

Run PowerShell as administrator and type:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 3. **Install dependencies**

```powershell
pip install -r requirements.txt
```

### 4. **Run server**

```powershell
python app.py
```

If successful, the server will be available at:

* [http://127.0.0.1:8000](http://127.0.0.1:8000)
* or local IP like [http://192.168.x.x:8000](http://192.168.x.x:8000)

---

## ⚙️ Adjusting Face Database Path (`LOCAL_DB_PATH`)

By default, the face database storage location is set directly in the `app.py` file via the `LOCAL_DB_PATH` variable. Example:

```python
LOCAL_DB_PATH = r"C:\Users\GYAN\Documents\Magang\Sinergi Merah Putih\Robo Pepper\Face_Database"
```

If you're running the application on another computer, make sure:

* **The folder path exists and is writable**
* If using a different folder, change the `LOCAL_DB_PATH` value in `app.py` according to your face folder location

Example replacement:

```python
# Replace with the appropriate folder on your system
LOCAL_DB_PATH = r"C:\Users\<YOUR_NAME>\Documents\Face_Database"
```

---

## 📄 License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

---

## 🙏 Attribution

If you use this code in your project, please provide attribution by mentioning the original author and linking back to this repository. This project represents significant personal effort and was developed as part of an Apple Developer Academy application portfolio.

---

For further questions, please open an issue in this repository or contact the maintainer.
