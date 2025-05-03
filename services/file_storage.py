import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import tempfile
import shutil
from pathlib import Path
from db.db_manager import get_connection  # Corrected import statement


class FileStorageSystem:
    def __init__(self, storage_path=None):
        self.storage_path = storage_path or os.path.expanduser('~/.vault_storage')
        os.makedirs(self.storage_path, exist_ok=True)

    def _generate_aes_key(self):
        """Generate a random 256-bit (32-byte) AES key"""
        return secrets.token_bytes(32)

    def _pad_data(self, data):
        """Pad data to be a multiple of the block size"""
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(data) + padder.finalize()
        return padded_data

    def _unpad_data(self, data):
        """Remove padding from data"""
        unpadder = padding.PKCS7(128).unpadder()
        unpadded_data = unpadder.update(data) + unpadder.finalize()
        return unpadded_data

    def encrypt_file(self, source_path, key):
        """
        Encrypt a file and save it to the vault storage
        Returns the path to the encrypted file
        """
        encrypted_filename = f"{secrets.token_hex(16)}.enc"
        encrypted_path = os.path.join(self.storage_path, encrypted_filename)
        iv = secrets.token_bytes(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()

        with open(source_path, 'rb') as f_in, open(encrypted_path, 'wb') as f_out:
            f_out.write(iv)
            while True:
                chunk = f_in.read(64 * 1024)
                if not chunk:
                    break
                padded_chunk = self._pad_data(chunk)
                encrypted_chunk = encryptor.update(padded_chunk)
                f_out.write(encrypted_chunk)
            f_out.write(encryptor.finalize())

        return encrypted_path

    def decrypt_file(self, encrypted_path, key, output_path=None):
        """
        Decrypt a file to a temporary location or specified output path
        Returns the path to the decrypted file
        """
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            original_filename = os.path.basename(encrypted_path).replace('.enc', '')
            output_path = os.path.join(temp_dir, original_filename)

        with open(encrypted_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            iv = f_in.read(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            while True:
                chunk = f_in.read(64 * 1024)
                if not chunk:
                    break
                decrypted_chunk = decryptor.update(chunk)
                if len(chunk) < 64 * 1024:
                    decrypted_chunk = self._unpad_data(decrypted_chunk)
                f_out.write(decrypted_chunk)

            final_chunk = decryptor.finalize()
            if final_chunk:
                final_chunk = self._unpad_data(final_chunk)
                f_out.write(final_chunk)

        return output_path

    def add_file_to_vault(self, user_id, source_path, filename=None):
        """Add a file to the vault for a specific user"""
        if filename is None:
            filename = os.path.basename(source_path)

        conn = get_connection()
        cursor = conn.cursor()

        try:
            # Get or create user's encryption key
            cursor.execute("SELECT encrypted_key FROM users WHERE id = %s", (user_id,))
            result = cursor.fetchone()

            if result and result[0]:
                key = result[0]  # Assuming key is stored as binary in MySQL
            else:
                key = self._generate_aes_key()
                cursor.execute(
                    "UPDATE users SET encrypted_key = %s WHERE id = %s",
                    (key, user_id))
                conn.commit()

            # Encrypt and store the file
            encrypted_path = self.encrypt_file(source_path, key)

            # Add to database
            cursor.execute(
                "INSERT INTO files (user_id, filename, filepath) VALUES (%s, %s, %s)",
                (user_id, filename, encrypted_path))
            conn.commit()

            return cursor.lastrowid
        finally:
            cursor.close()

    def open_file_from_vault(self, file_id, user_id):
        """Open a file from the vault"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT filepath FROM files WHERE id = %s AND user_id = %s",
                (file_id, user_id))
            result = cursor.fetchone()

            if not result:
                raise ValueError("File not found or access denied")

            cursor.execute(
                "SELECT encrypted_key FROM users WHERE id = %s",
                (user_id,))
            key_result = cursor.fetchone()

            if not key_result or not key_result['encrypted_key']:
                raise ValueError("User key not found")

            encrypted_path = result['filepath']
            key = key_result['encrypted_key']
            temp_path = self.decrypt_file(encrypted_path, key)

            # Open with default program
            try:
                if os.name == 'nt':
                    os.startfile(temp_path)
                elif os.name == 'posix':
                    if os.uname().sysname == 'Darwin':
                        os.system(f'open "{temp_path}"')
                    else:
                        os.system(f'xdg-open "{temp_path}"')
            except Exception as e:
                os.remove(temp_path)
                raise e
        finally:
            cursor.close()

    def delete_file_from_vault(self, file_id, user_id):
        """Delete a file from the vault"""
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        try:
            cursor.execute(
                "SELECT filepath FROM files WHERE id = %s AND user_id = %s",
                (file_id, user_id))
            result = cursor.fetchone()

            if not result:
                raise ValueError("File not found or access denied")

            encrypted_path = result['filepath']

            # Delete from filesystem
            try:
                os.remove(encrypted_path)
            except OSError:
                pass

            # Delete from database
            cursor.execute(
                "DELETE FROM files WHERE id = %s AND user_id = %s",
                (file_id, user_id))
            conn.commit()
        finally:
            cursor.close()
