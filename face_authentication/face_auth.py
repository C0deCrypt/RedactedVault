import cv2
import face_recognition
from cryptography.fernet import Fernet
from db.db_manager import get_connection
import numpy as np


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


def get_user_encoding(username):
    """Fetch encrypted face encoding for a specific username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.data
        FROM users u
        JOIN biometric_data b ON u.id = b.user_id
        WHERE u.username = %s AND b.type = 'face'
    """, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0] if result else None


def get_user_unlock_code(username):
    """Fetch the unlock code for a specific username."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT unlock_code
        FROM vault_settings
        WHERE user_id = (
            SELECT id FROM users WHERE username = %s
        )
    """, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    return result[0] if result else None


def authenticate_face(username):
    print("Face Authentication")

    # Get the encrypted face encoding and unlock code from DB
    encrypted_data = get_user_encoding(username)
    unlock_code = get_user_unlock_code(username)

    if not encrypted_data:
        print("No face data found for this username.")
        return False

    if not unlock_code:
        print("No unlock code found for this username.")
        return False

    key = load_key()

    try:
        known_encoding = decrypt_encoding(encrypted_data, key)
    except Exception as e:
        print(f"Error decrypting data for {username}: {e}")
        return False

    # Begin face authentication process
    cap = cv2.VideoCapture(0)
    print("Press 's' to scan your face for authentication.")
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
                    print(f"Welcome back, {username}!")
                    auth_success = True
                else:
                    print("Face does not match this username.")
            else:
                print("No face detected. Try again.")
            break

    cap.release()
    cv2.destroyAllWindows()

    if auth_success:
        print("Now, please enter the unlock code:")
        entered_code = input()

        if entered_code == unlock_code:
            print("Authentication successful! Vault opened.")
            return True
        else:
            print("Invalid unlock code.")
            return False

    return auth_success


if __name__ == "__main__":
    username = input("Enter your username: ")
    authenticate_face(username)
