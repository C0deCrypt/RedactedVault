import os
from db.db_manager import (
    get_user_vault_settings,
    add_file_to_db,
    get_file_from_db,
    delete_file_from_db,
    log_vault_access
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

        # Get user's vault settings which contains the encrypted AES key
        vault_settings = get_user_vault_settings(user_id)
        if not vault_settings:
            raise ValueError("User vault not initialized")

        # Here you would need to decrypt the AES key using biometric authentication
        # For now, we'll assume it's already decrypted and passed to this method
        # In a real implementation, you would get the decrypted key from the auth process
        key = vault_settings.get('decrypted_aes_key')
        if not key:
            raise ValueError("No decryption key available")

        # Encrypt and save to database
        encrypted_path = self.storage.encrypt_file(source_path, key)
        file_id = add_file_to_db(user_id, filename, encrypted_path)

        # Log the file addition
        log_vault_access(user_id, 'file_add', f"Added file: {filename}")

        return file_id

    def open_file_from_vault(self, file_id, user_id):
        """Open a vault file (decrypts it temporarily)"""
        file_record = get_file_from_db(file_id, user_id)
        if not file_record:
            raise ValueError("File not found")

        # Get user's vault settings which contains the encrypted AES key
        vault_settings = get_user_vault_settings(user_id)
        if not vault_settings:
            raise ValueError("User vault not initialized")

        # Again, assuming decrypted key is available
        key = vault_settings.get('decrypted_aes_key')
        if not key:
            raise ValueError("No decryption key available")

        # Decrypt and open the file
        decrypted_path = self.storage.decrypt_file(file_record['filepath'], key)
        temp_dir = self.storage.open_decrypted_file(decrypted_path)

        # Log the file access
        log_vault_access(user_id, 'file_open', f"Opened file: {file_record['filename']}")

        return temp_dir

    def delete_file_from_vault(self, file_id, user_id):
        """Permanently delete a file from vault"""
        file_record = get_file_from_db(file_id, user_id)
        if not file_record:
            raise ValueError("File not found")

        # Delete both the file and database record
        self.storage.delete_encrypted_file(file_record['filepath'])
        delete_file_from_db(file_id, user_id)

        # Log the file deletion
        log_vault_access(user_id, 'file_delete', f"Deleted file: {file_record['filename']}")

    def cleanup_temp_files(self, temp_dir):
        """Clean up temporary decrypted files"""
        self.storage.cleanup_temp_files(temp_dir)