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
## Project Flow

<img width="1917" height="917" alt="1" src="https://github.com/user-attachments/assets/b90d3f62-4031-43fd-8423-e819a7e282e9" />
<img width="1918" height="906" alt="2" src="https://github.com/user-attachments/assets/481237d7-708a-42b0-ad8c-05ed54340ee5" />

<img width="1919" height="916" alt="3" src="https://github.com/user-attachments/assets/cad75383-a9da-426c-8760-ff66f33478ad" />

<img width="1916" height="912" alt="4" src="https://github.com/user-attachments/assets/d71ad9af-1cba-475f-8d75-f511c95cc58e" />
<img width="1823" height="870" alt="5" src="https://github.com/user-attachments/assets/466fea16-09e9-4f9f-9704-3f0e7c7c6895" />


<img width="1919" height="923" alt="6" src="https://github.com/user-attachments/assets/f3fa4ee6-22cc-4ad2-b5c1-c4efee5cd636" />


<img width="1919" height="965" alt="8" src="https://github.com/user-attachments/assets/b3356321-aaa8-4e74-8288-e92d477b8a0f" />

<img width="1919" height="933" alt="7" src="https://github.com/user-attachments/assets/1be70b98-654d-4e3d-8124-252e9bd68e03" />
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
