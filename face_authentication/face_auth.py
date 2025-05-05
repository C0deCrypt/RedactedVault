# auth_manager.py

import cv2
import face_recognition
import numpy as np
from cryptography.fernet import Fernet
from db.db_manager import fetch_user_biometric, get_user_unlock_code

def load_key():
    """Load the saved encryption key."""
    with open("../gui/secret.key", "rb") as key_file:
        return key_file.read()


def decrypt_encoding(encrypted_data, key):
    """Decrypt the encrypted face encoding."""
    fernet = Fernet(key)
    decrypted_bytes = fernet.decrypt(encrypted_data)
    encoding_list = list(map(float, decrypted_bytes.decode().split(',')))
    return np.array(encoding_list)


def authenticate_face(username):
    print("🔐 Face Authentication")

    # Load key and fetch data from DB
    key = load_key()
    encrypted_data = None
    unlock_code = None

    try:
        user_id, encrypted_data = fetch_user_biometric(username, 'face')
        unlock_code = get_user_unlock_code(username)
    except Exception as e:
        print(f"Error accessing user data: {e}")
        return False

    if not encrypted_data:
        print("No face data found for this user.")
        return False

    if not unlock_code:
        print("No unlock code found for this user.")
        return False

    try:
        known_encoding = decrypt_encoding(encrypted_data, key)
    except Exception as e:
        print(f"Decryption failed: {e}")
        return False

    # Begin face capture
    cap = cv2.VideoCapture(0)
    print("📷 Press 's' to scan your face for authentication.")
    auth_success = False

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Face Authentication", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)

            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb, face_locations)[0]
                match = face_recognition.compare_faces([known_encoding], face_encoding)[0]

                if match:
                    print(f"✅ Face matched. Welcome, {username}!")
                    auth_success = True
                else:
                    print("❌ Face mismatch.")
            else:
                print("⚠️ No face detected. Try again.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if auth_success:
        print("✅ Authentication successful. Vault opened.")
        return True
    else:
        print("❌ Error occured")
        return False

    return False


if __name__ == "__main__":
    username = input("Enter your username: ")
    authenticate_face(username)
