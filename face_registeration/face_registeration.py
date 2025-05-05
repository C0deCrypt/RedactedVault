import cv2
import face_recognition
from cryptography.fernet import Fernet
import os
from db.db_manager import set_current_user, get_current_user_id, get_user_encryption_key, register_user_to_database
from db.db_manager import log_access

# Secret code trigger
SECRET_TRIGGER = "0000+-"


expression = ""

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

def register_face(username):
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
        # Get or generate encryption key
        generate_key()
        key = load_key()


        # Convert face encoding to a string (required for encryption)
        encoding_str = ','.join(map(str, face_encoding))

        # Encrypt the face encoding data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(encoding_str.encode())

        # Save encrypted data to the database
        print("Saving face data to the database...")
        register_user_to_database(username, "face", encrypted_data)


        # logs will be saved for file crud and logins NOT REGISTER
        # log_access("face_registration", f"Face registered for {username}")

        print(f"🎉 {username} registered successfully!")
        return True
    else:
        print("❌ Face registration failed.")
        return False


if __name__ == "__main__":
    username = input("Enter your username to register: ")

    # Set the current user (assuming you already have authentication logic in place)
    set_current_user(username, 1)  # Here 1 is a placeholder for user_id

    # Register the face
    register_face(username)
