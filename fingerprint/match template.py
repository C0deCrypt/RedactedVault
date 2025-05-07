import os
import sys
import json
import numpy as np
from cryptography.fernet import Fernet
from match_utils import preprocess_fingerprint, extract_minutiae, compare_minutiae
from db.db_manager import fetch_user_biometric, get_user_unlock_code

IMG_WIDTH, IMG_HEIGHT = 260, 300
FINGERPRINT_DIR = os.path.join("fingerprint", "fingerprints")

def load_key():
    """Load Fernet master key."""
    with open("secret.key", "rb") as key_file:
        return key_file.read()

def authenticate_fingerprint(username):
    print("🔐 Fingerprint Authentication")

    # === Load encrypted minutiae from DB ===
    key = load_key()
    user_id, encrypted_data = fetch_user_biometric(username, "finger")

    if not encrypted_data:
        print("❌ No fingerprint data found.")
        return False

    unlock_code = get_user_unlock_code(username)
    if not unlock_code:
        print("❌ Unlock code missing.")
        return False

    # === Load fingerprint scan ===
    fingerprint_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "fingerprints", f"{username}_live.dat"))
    if not os.path.exists(fingerprint_path):
        print("❌ Fingerprint scan not found.")
        return False

    with open(fingerprint_path, "rb") as f:
        raw = f.read()

    if len(raw) != IMG_WIDTH * IMG_HEIGHT:
        print("❌ Invalid fingerprint size.")
        return False

    img = np.frombuffer(raw, dtype=np.uint8).reshape((IMG_HEIGHT, IMG_WIDTH))
    skeleton = preprocess_fingerprint(img)
    live_minutiae = extract_minutiae(skeleton)

    if len(live_minutiae) < 10:
        print("❌ Poor fingerprint quality.")
        return False

    try:
        fernet = Fernet(key)
        stored_minutiae = json.loads(fernet.decrypt(encrypted_data).decode())
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        return False

    # === Matching ===
    matches, total1, total2 = compare_minutiae(live_minutiae, stored_minutiae)
    ratio = matches / max(len(stored_minutiae), 1)

    print(f"[DEBUG] Matches: {matches}, Ratio: {ratio:.3f}")

    if ratio > 0.60:
        print("✅ Fingerprint match successful.")
        return True
    else:
        print("❌ Fingerprint mismatch.")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python match_template.py <username>")
        sys.exit(1)

    username = sys.argv[1]
    success = authenticate_fingerprint(username)

    if success:
        print("AUTH_SUCCESS")
        sys.exit(0)
    else:
        print("AUTH_FAIL")
        sys.exit(1)
