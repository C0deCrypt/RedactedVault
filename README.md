# 🔐 RedactedVault – Hidden Vault Behind a Fake Calculator

> _"What looks like a calculator, acts like a calculator, but hides your secrets like a pro?" – RedactedVault._

## 🧠 Overview

**RedactedVault** is a stealthy, secure vault application disguised as a regular calculator. It looks innocent on the surface, but when a secret code is entered, it unlocks a hidden vault protected by **biometric authentication** using our custom-built **[Auth2X](https://github.com/C0deCrypt/Auth2X)** system.

This app is designed for privacy-focused users who want their files stored securely and discreetly using AES encryption, facial recognition, and fingerprint verification.

---

## 🚀 Key Features

- 🧮 **Fully Functional Calculator**  
  Launches as a regular calculator with standard arithmetic operations.

- 🔑 **Secret Code Trigger**  
  - `0000+-` → Opens **User Registration** window.
  - `[Your custom vault code]` → Opens **Authentication** screen.

- 🧍 **User Registration Flow**
  - Set your **username** and **secret vault code**.
  - The code is stored and later used to access your private vault.
  
- 🔐 **Biometric Authentication (via Auth2X)**
  - **Face Recognition** using OpenCV + 128D Face Encodings
  - **Fingerprint Verification** using SecuGen SDK + Minutiae Matching
  - Encrypted biometric data storage using **Fernet (AES)** encryption
  - Stored securely in a **MySQL database**

- 🗂️ **Encrypted Vault System**
  - Add files to your vault (AES-encrypted using Fernet).
  - Files are renamed randomly and stored in a **hidden folder**.
  - Metadata (original name, file ID, timestamp) is saved in DB.

- 🧾 **View Files**
  - Files are decrypted **temporarily** for viewing.
  - Auto-deleted securely after viewing.

- 🗑️ **Delete Files**
  - Remove unwanted files from the vault.

- 🔒 **Lock the Vault**
  - One-click vault lock and return to calculator mode.

---

## 🛡️ Auth2X Biometric System (Integrated)

**RedactedVault** integrates the [Auth2X](https://github.com/C0deCrypt/Auth2X) biometric system for secure and encrypted authentication.

### 🔐 Auth2X Highlights:
- 🔍 Face Recognition using `face_recognition` + Fernet-encrypted 128D encodings.
- 🧬 Fingerprint Matching using:
  - SecuGen SDK for fingerprint capture
  - Custom minutiae extraction
  - Match ratio-based verification (> 0.65 for success)
- 💾 MySQL-based encrypted biometric data storage
- 🛠️ Modular C++ EXE for fingerprint capture and GUI-based auth flows.

For more technical details, biometric implementation, and database schema, check the complete [Auth2X documentation here](https://github.com/C0deCrypt/Auth2X).

---

## 🧑‍💻 Contributors

| Name              | Contribution                          |
|-------------------|----------------------------------------|
| **Ayaan Ahmed Khan**  | Vault Logic + GUI Design + File Encryption & Handling |
| **Muhammad Talal** | Vault Logic + File Encryption & Handling |
| **Ramlah Munir**  | Integrated Fingerprint Auth (Auth2X) |
| **Mohammad Umar Nasir** | Face Auth Integration (Auth2X) + Calculator Logic |


---

## ⚙️ Tech Stack

- **Frontend/UI:** Tkinter (Python GUI)
- **Backend:** Python, C++
- **Database:** MySQL
- **Encryption:** Fernet (AES-128)
- **Face Recognition:** OpenCV + face_recognition
- **Fingerprint:** SecuGen SDK + Custom Matcher

---

## 📂 Folder Structure


````

RedactedVault/
├── db/
│   └── db_manager.py         # Handles DB operations (fetch/save user/files)
├── face_authentication/
│   └── face_auth.py          # Handles face authentication logic
├── fac_registeration/
│   ├── face_registeration.py
│   └── secret.key            
├── gui/
│   ├── vault.py              # Vault logic: encryption, file ops, viewing
│   ├── authenticate_window.py
│   ├── fakecalculator.py     # 🔹 Entry point: Main calculator app
│   ├── register_window\.py   
│   ├── secret.key       

````

---

## 🧪 How to Run

 **Install dependencies:**

```bash
pip install pillow face_recognition opencv-python cryptography mysql-connector-python sv-ttk numpy
````
> 💡 Don't forget to also install and configure **MySQL Server** locally and set up the `.env` file correctly.

 **Run the app:**
> 🔹 **Run** : `gui/fakecalculator.py`



---

## 💡 Future Enhancements

* Add **multi-user support**
* Vault backup/export options
* Face/fingerprint fallback mechanism
* PyInstaller packaging for `.exe` delivery

---

## 📬 Contact

For collaboration, questions, or demos, feel free to connect with us:

* **Face & Fingerprint Auth:**
  [Ramlah's LinkedIn](https://www.linkedin.com/in/ramlah-munir-6b2320344)
  [Umar's LinkedIn](https://www.linkedin.com/in/mohammad-umar-nasir)

* **Vault & GUI Development:**
  [Ayaan's LinkedIn](https://www.linkedin.com/in/ayaan-ahmed-khan-448600351)
  [Talal's LinkedIn](https://www.linkedin.com/in/muhammad-talal-1675a0351)

---
> *“Not everything is as it seems. Especially not your calculator.” – RedactedVault*
---
