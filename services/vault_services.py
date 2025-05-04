import os
from db.db_manager import (
    get_user_encryption_key,
    update_user_encryption_key,
    add_file_to_db,
    get_file_from_db,
    delete_file_from_db,
    get_connection
)
from services.file_storage import FileStorageSystem


class VaultService:
    def __init__(self):
        """Initialize the vault service with storage system"""
        self.storage = FileStorageSystem()
        self._verified_users = set()

    def _ensure_user_exists(self, user_id):
        """Verify and create user if doesn't exist"""
        if user_id not in self._verified_users:
            conn = get_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO users (id, biometric_hash) VALUES (%s, '')",
                        (user_id,)
                    )
                    conn.commit()
                self._verified_users.add(user_id)
            finally:
                cursor.close()

    def add_file_to_vault(self, user_id, source_path, filename=None):
        """Add file to vault with automatic user creation"""
        try:
            self._ensure_user_exists(user_id)

            if not os.path.exists(source_path):
                raise ValueError("Source file does not exist")

            filename = filename or os.path.basename(source_path)
            key = get_user_encryption_key(user_id)
            if not key:
                key = self.storage._generate_aes_key()
                update_user_encryption_key(user_id, key)

            encrypted_path = self.storage.encrypt_file(source_path, key)
            return add_file_to_db(user_id, filename, encrypted_path)

        except Exception as e:
            raise ValueError(f"Failed to add file: {str(e)}")

    def open_file_from_vault(self, file_id, user_id):
        """Open a file from vault (decrypt temporarily)"""
        try:
            self._ensure_user_exists(user_id)

            file_record = get_file_from_db(file_id, user_id)
            if not file_record:
                raise ValueError("File not found or access denied")

            key = get_user_encryption_key(user_id)
            if not key:
                raise ValueError("Encryption key not found")

            decrypted_path = self.storage.decrypt_file(file_record['filepath'], key)
            return self.storage.open_decrypted_file(decrypted_path)

        except Exception as e:
            raise ValueError(f"Failed to open file: {str(e)}")

    def delete_file_from_vault(self, file_id, user_id):
        """Permanently delete file from vault"""
        try:
            self._ensure_user_exists(user_id)

            file_record = get_file_from_db(file_id, user_id)
            if not file_record:
                raise ValueError("File not found or access denied")

            self.storage.delete_encrypted_file(file_record['filepath'])
            delete_file_from_db(file_id, user_id)

        except Exception as e:
            raise ValueError(f"Failed to delete file: {str(e)}")

    def cleanup_temp_files(self, temp_dir):
        """Clean up temporary decrypted files"""
        try:
            self.storage.cleanup_temp_files(temp_dir)
        except Exception as e:
            raise ValueError(f"Failed to clean temp files: {str(e)}")