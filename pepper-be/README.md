# 🚀 Pepper Robot Management Backend

A Python Flask-based backend for managing Pepper robot functionality.

> **Note**: This project was originally developed as part of an Apple Developer Academy application portfolio and represents significant personal effort. While it's open source under MIT License, please provide proper attribution when using this code.

---

## 📋 Requirements

* **Python 3.11.1** (Install instructions below)
* **pip** (comes with Python)
* Internet connection

---

## 🧑‍💻 Step-by-Step Setup (For Beginners)

### 1. 🔧 Install Python 3.11.1

If you don't have Python installed yet:

* Visit the official page:
  👉 [https://www.python.org/downloads/release/python-3111/](https://www.python.org/downloads/release/python-3111/)

* Download **Windows installer (64-bit)**.

* During installation:

  * ✅ **Check** the box that says **"Add Python to PATH"**
  * Then click **Install Now**

* After installing, open **Command Prompt (CMD)** and run:

  ```bash
  python --version
  ```

  You should see something like:

  ```
  Python 3.11.1
  ```

---

### 2. 📥 Clone this repository

```bash
git clone https://github.com/Sinergi-MP/pepper-robot-management-be.git
cd pepper-robot-management-be
```

---

### 3. 🔄 Switch to the development branch

You can use either of the following:

```bash
git checkout dev
```

Or if you want to create the branch locally:

```bash
git checkout -b dev
```

---

### 4. 🧪 Set up a virtual environment (to isolate dependencies)

#### 👉 Windows (CMD):

```bash
python -m venv venv
venv\Scripts\activate
```

#### 👉 Windows (PowerShell):

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

Once activated, your terminal will show something like:

```
(venv) C:\Users\YourName\pepper-robot-management-be>
```

---

### 5. 📦 Install the required Python packages

```bash
pip install -r requirements.txt
```

---

### 6. 🔐 Ask the dev team for secrets

Request these files from the development team:

* `.env`
* `keycredentials.json` (for Google Cloud Platform access)

Place them in the project root directory.

---

### 7. ▶️ Run the Flask app

```bash
python run.py
```

By default, it will be accessible at:
🌐 [http://localhost:5000](http://localhost:5000)

---

### 8. ❌ Deactivate the virtual environment (when you're done)

```bash
deactivate
```

---

## 🧠 Need Help?

If you run into any problems, feel free to ask the development team for support or open an issue in this repository.

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