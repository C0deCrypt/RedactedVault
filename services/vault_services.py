import os
from db.db_manager import (
    get_user_encryption_key,
    update_user_encryption_key,
    add_file_to_db,
    get_file_from_db,
    delete_file_from_db
)
from services.file_storage import FileStorageSystem


class VaultService:
    def __init__(self):
        self.storage = FileStorageSystem()

    def add_file_to_vault(self, user_id, source_path, filename=None):
        """Save a file to the vault (encrypts it first)"""
        if not os.path.exists(source_path):
            raise ValueError("File doesn't exist")

        # Use original filename if none provided
        filename = filename or os.path.basename(source_path)

        # Get user's key or make a new one
        key = get_user_encryption_key(user_id)
        if not key:
            key = self.storage._generate_aes_key()
            update_user_encryption_key(user_id, key)

        # Encrypt and save to database
        encrypted_path = self.storage.encrypt_file(source_path, key)
        return add_file_to_db(user_id, filename, encrypted_path)

    def open_file_from_vault(self, file_id, user_id):
        """Open a vault file (decrypts it temporarily)"""
        file_record = get_file_from_db(file_id, user_id)
        if not file_record:
            raise ValueError("File not found")

        key = get_user_encryption_key(user_id)
        if not key:
            raise ValueError("No key found")

        # Decrypt and open the file
        decrypted_path = self.storage.decrypt_file(file_record['filepath'], key)
        return self.storage.open_decrypted_file(decrypted_path)

    def delete_file_from_vault(self, file_id, user_id):
        """Permanently delete a file from vault"""
        file_record = get_file_from_db(file_id, user_id)
        if not file_record:
            raise ValueError("File not found")

        # Delete both the file and database record
        self.storage.delete_encrypted_file(file_record['filepath'])
        delete_file_from_db(file_id, user_id)

    def cleanup_temp_files(self, temp_dir):
        """Clean up temporary decrypted files"""
        self.storage.cleanup_temp_files(temp_dir)