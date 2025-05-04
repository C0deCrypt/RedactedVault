import os
import secrets
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import tempfile
import shutil
from pathlib import Path


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

    def open_decrypted_file(self, decrypted_path):
        """Open decrypted file with default program and return temp directory for cleanup"""
        try:
            if os.name == 'nt':
                os.startfile(decrypted_path)
            elif os.name == 'posix':
                if os.uname().sysname == 'Darwin':
                    os.system(f'open "{decrypted_path}"')
                else:
                    os.system(f'xdg-open "{decrypted_path}"')

            # Return the temp directory containing the file for later cleanup
            return os.path.dirname(decrypted_path)
        except Exception as e:
            # Clean up if opening fails
            temp_dir = os.path.dirname(decrypted_path)
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise e

    def cleanup_temp_files(self, temp_dir):
        """Clean up temporary decrypted files"""
        shutil.rmtree(temp_dir, ignore_errors=True)

    def delete_encrypted_file(self, encrypted_path):
        """Delete encrypted file from storage"""
        try:
            os.remove(encrypted_path)
        except OSError:
            pass