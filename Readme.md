# 📱 Flask Encrypted Messaging App

A secure and fun messaging web app built with **Flask** that allows users to:

* Log in using OTP verification
* Manage contacts
* Send normal or **encrypted messages** hidden inside images using **steganography**
* Auto-delete messages after decryption (ephemeral messaging system)

---

## 🚀 Features

* 🔐 **OTP-based Authentication** — Users log in using their phone number and a one-time password (OTP).
* 💬 **Contact Management** — Add and list your personal contacts.
* 🖼️ **Encrypted Image Messaging** — Messages can be hidden inside sticker images using steganography (Pillow).
* 🧩 **Decryption Code** — A unique code is required to reveal the hidden message.
* ⏱️ **Auto-Delete** — Messages can self-delete after a specified time (e.g., 15 seconds).
* 🗄️ **SQLite Database** — Lightweight storage for users, contacts, and messages.

---

## 🧰 Tech Stack

* **Backend:** Flask (Python)
* **Database:** SQLite
* **Frontend:** HTML (templates), JavaScript, CSS
* **Libraries Used:**

  * `Flask`
  * `sqlite3`
  * `Pillow`
  * `base64`
  * `io`, `json`, `random`, `string`, `datetime`

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository

```bash
git clone https://github.com/<your-username>/<your-repo-name>.git
cd <your-repo-name>
```

### 2️⃣ Create a virtual environment

```bash
python -m venv .venv
source .venv/Scripts/activate   # On Windows
# or
source .venv/bin/activate       # On macOS/Linux
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the app

```bash
python app.py
```

App will be available at:

```
http://localhost:5000
```

---

## 📂 Project Structure

```
.
├── app.py                 # Main Flask application
├── messaging_app.db       # SQLite database (auto-created)
├── static/
│   └── images/            # Sticker images used for steganography
├── templates/
│   ├── login.html
│   └── dashboard.html
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

1. **User Login:**

   * Enter your phone number → receive OTP → verify.

2. **Contacts:**

   * Add new contacts by name and phone number.

3. **Send Message:**

   * Choose whether to send a normal or **encrypted sticker** message.
   * If encrypted, the system hides the text inside a random image.

4. **Decryption:**

   * The receiver must enter the **decryption code** to reveal the hidden message.

5. **Auto-Delete:**

   * Once decrypted, the message is automatically deleted after 15 seconds.

---

## 🖼️ Stickers

Place your sticker images in:

```
static/images/
```

If no stickers are found, a fallback sticker will be automatically generated.

---

## ⚠️ Important Notes

* The OTP system is simulated for demo purposes — OTPs are printed in the response and not sent via SMS.
* This app runs in **debug mode**. Disable debug mode before deploying to production.
* Always update the Flask `secret_key` in `app.py` before going live.

---

## 🧑‍💻 Author

**Developed by:** [Roshan Pandit]
📧 Contact: [roshanpandit8300@gmail.com](mailto:roshanpandit8300@gmail.com)


---

## 📜 License

This project is licensed under the **MIT License** — feel free to use, modify, and share it.
