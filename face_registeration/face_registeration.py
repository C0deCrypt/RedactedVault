import cv2
import face_recognition
from cryptography.fernet import Fernet
import os
from db.db_manager import set_current_user, get_current_user_id, add_file_to_vault, get_user_encryption_key
from db.db_manager import log_access

# Secret code trigger
SECRET_TRIGGER = "0000+-"

# Colors
BG = "#1C1C1C"
TEXT = "#F5E8D8"
CORAL = "#FF6F61"
GOLD = "#DAA520"
HOVER = "#FF4500"
BORDER = "#333333"
BTN_BG = "#252525"
EQUAL_BTN = "#FF6F00"
EQUAL_HOVER = "#FF8C00"

expression = ""


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
        key = get_user_encryption_key(get_current_user_id())
        if not key:
            key = Fernet.generate_key()  # Generate a new key if not found
            # Save the key to the database (this should be handled securely)
            # Update user's encryption key (you should already have user ID set after authentication)
            # save_user_encryption_key(get_current_user_id(), key)

        # Convert face encoding to a string (required for encryption)
        encoding_str = ','.join(map(str, face_encoding))

        # Encrypt the face encoding data
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(encoding_str.encode())

        # Save encrypted data to the database
        print("Saving face data to the database...")
        # You could modify this function to save the face data directly, or use a similar structure to storing files
        file_id = add_file_to_vault(get_current_user_id(), encrypted_data, "face_encoding.dat")
        print(f"Face encoding saved to vault with file ID: {file_id}")

        # Optional: Log the registration attempt
        log_access("face_registration", f"Face registered for {username}")

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
