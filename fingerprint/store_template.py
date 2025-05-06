import sys
import os
import json
import numpy as np
from cryptography.fernet import Fernet
from match_utils import preprocess_fingerprint, extract_minutiae
from db.db_manager import register_user_to_database

def generate_aes_key():
    return os.urandom(32)  # 256-bit AES key

def encrypt_aes_key(aes_key, master_key):
    fernet = Fernet(master_key)
    return fernet.encrypt(aes_key)

def generate_key_if_missing():
    if not os.path.exists("secret.key"):
        with open("secret.key", "wb") as f:
            f.write(Fernet.generate_key())

def load_key():
    with open("secret.key", "rb") as f:
        return f.read()

def main():
    if len(sys.argv) != 3:
        print("Usage: python store_template.py <username> <unlock_code>")
        sys.exit(1)

    username = sys.argv[1]
    unlock_code = sys.argv[2]

    IMG_WIDTH, IMG_HEIGHT = 260, 300
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fingerprint_path = os.path.join(base_dir, "fingerprints", f"{username}.dat")

    if not os.path.exists(fingerprint_path):
        print(f"[ERROR] Fingerprint file not found: {fingerprint_path}")
        sys.exit(1)

    with open(fingerprint_path, "rb") as f:
        raw_data = f.read()

    img = np.frombuffer(raw_data, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))
    skeleton = preprocess_fingerprint(img)
    minutiae = extract_minutiae(skeleton)

    # Encrypt minutiae
    generate_key_if_missing()
    key = load_key()
    fernet = Fernet(key)

    minutiae_json = json.dumps(minutiae)
    encrypted_data = fernet.encrypt(minutiae_json.encode())

    # Generate and encrypt AES key
    aes_key = generate_aes_key()
    encrypted_aes_key = encrypt_aes_key(aes_key, key)

    # Save all to DB
    register_user_to_database(
        username=username,
        biometric_type="fingerprint",
        encrypted_data=encrypted_data,
        unlock_code=unlock_code,
        encrypted_aes_key=encrypted_aes_key
    )

    print(f"[SUCCESS] Fingerprint registered for '{username}'.")

if __name__ == "__main__":
    main()
