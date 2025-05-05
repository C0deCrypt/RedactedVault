import cv2
import face_recognition
from cryptography.fernet import Fernet
import os
from db.db_manager import set_current_user, get_current_user_id, get_user_encryption_key, register_user_to_database

# Secret code trigger
SECRET_TRIGGER = "0000+-"


expression = ""
def generate_aes_key():
    """Generate a 256-bit (32-byte) AES key."""
    return os.urandom(32)


def encrypt_aes_key(aes_key, master_key):
    """Encrypt the AES key using the master Fernet key."""
    fernet = Fernet(master_key)
    return fernet.encrypt(aes_key)
def generate_key():
    """Generate a new encryption key if not already present."""
    if not os.path.exists("secret.key"):
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)

def load_key():
    """Load the saved encryption key."""
    with open("secret.key", "rb") as key_file:
        return key_file.read()

def register_face(username,code):
    """Function to register a user face and store the data in the database."""
    print("=== Face Registration ===")

    cap = cv2.VideoCapture(0)
    print("📷 Press 's' to capture your face.")

    face_encoding = None

    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        cv2.imshow("Face Registration", frame)

        if cv2.waitKey(1) & 0xFF == ord('s'):
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb)

            if face_locations:
                face_encoding = face_recognition.face_encodings(rgb, face_locations)[0]
                print("✅ Face captured.")
                break
            else:
                print("❌ No face detected. Please try again.")

    cap.release()
    cv2.destroyAllWindows()

    if face_encoding is not None:
        # Ask user for unlock code
        unlock_code = code

        # Get or generate encryption key
        generate_key()
        key = load_key()

        # Generate and encrypt AES key
        aes_key = generate_aes_key()
        encrypted_aes_key = encrypt_aes_key(aes_key, key)

        # Convert face encoding to a string (required for encryption)
        encoding_str = ','.join(map(str, face_encoding))

        # Encrypt the face encoding data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(encoding_str.encode())

        # Save encrypted data and unlock code to the database
        print("Saving face data to the database...")
        register_user_to_database(username, "face", encrypted_data, unlock_code, encrypted_aes_key)

        print(f"🎉 {username} registered successfully!")
        return True
    else:
        print("❌ Face registration failed.")
        return False


if __name__ == "__main__":
    username = input("register working: ")


