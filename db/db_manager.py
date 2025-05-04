import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from services.file_storage import FileStorageSystem

# Initialize connection and user variables
_connection = None
_current_user = None
_current_user_id = None
_file_storage = FileStorageSystem()

def with_transaction(func):
    """Decorator for automatic transaction management"""
    def wrapper(*args, **kwargs):
        conn = get_connection()
        try:
            result = func(conn, *args, **kwargs)  # Note: conn is now passed
            conn.commit()
            return result
        except Exception as e:
            conn.rollback()
            raise
    return wrapper

def set_current_user(user, user_id):
    """Set the currently authenticated user"""
    global _current_user, _current_user_id
    _current_user = user
    _current_user_id = user_id


def get_current_user():
    """Get the current user's name"""
    return _current_user


def get_current_user_id():
    """Get the current user's ID"""
    return _current_user_id


def get_connection():
    """Get or create MySQL connection"""
    global _connection
    if not _connection or not _connection.is_connected():
        load_dotenv()
        try:
            _connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
        except Error as e:
            print(f"MySQL Error: {e}")
            raise
    return _connection


def close_connection():
    """Close active connection"""
    global _connection
    if _connection and _connection.is_connected():
        _connection.close()
        _connection = None


def get_files_for_user():
    """
    List files for the currently authenticated user.
    Raises ValueError if no user is currently set.
    Returns list of file dictionaries or empty list on error.
    """
    conn = get_connection()
    user_id = get_current_user_id()

    if not user_id:
        raise ValueError("Cannot fetch files - no authenticated user")

    try:
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, filename, filepath, 
                   DATE_FORMAT(date_added, '%Y-%m-%d %H:%i') as formatted_date
            FROM files 
            WHERE user_id = %s
            ORDER BY date_added DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()

    except Error as e:
        print(f"Error fetching files: {e}")
        return []

    finally:
        if 'cursor' in locals():
            cursor.close()

def get_user_encryption_key(user_id):
    """Retrieve user's encryption key from database"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT `encrypted_key` FROM `users` WHERE `id` = %s", (user_id,))
        result = cursor.fetchone()
        if not result:
            return None
        return result['encrypted_key']
    except mysql.connector.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        cursor.close()

@with_transaction
def update_user_encryption_key(conn, user_id, key):
    """Store/update user's encryption key in database"""
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE users SET encrypted_key = %s WHERE id = %s",
            (key, user_id))
    finally:
        cursor.close()

@with_transaction
def add_file_to_db(conn, user_id, filename, encrypted_path):
    """Store file metadata in database with transaction support"""
    cursor = conn.cursor()
    try:
        # Verify user exists
        cursor.execute("SELECT 1 FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            raise ValueError(f"User {user_id} does not exist")

        # Insert file record
        cursor.execute(
            "INSERT INTO files (user_id, filename, filepath) VALUES (%s, %s, %s)",
            (user_id, filename, encrypted_path))
        return cursor.lastrowid
    finally:
        cursor.close()
def get_file_from_db(file_id, user_id):
    """Retrieve file record if it belongs to the user"""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            "SELECT filepath FROM files WHERE id = %s AND user_id = %s",
            (file_id, user_id))
        return cursor.fetchone()
    finally:
        cursor.close()

def delete_file_from_db(file_id, user_id):
    """Remove file record from database"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "DELETE FROM files WHERE id = %s AND user_id = %s",
            (file_id, user_id))
        conn.commit()
    finally:
        cursor.close()

def log_access(event_type, details=None, user_id=None):
    """Record access attempts (uses current user if no ID provided)"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        user_to_log = user_id if user_id else get_current_user_id()

        if not user_to_log:
            raise ValueError("No user ID provided and no current user set")

        query = """
            INSERT INTO vault_access_logs 
            (user_id, event_type, details)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_to_log, event_type, details))
        conn.commit()
    except Error as e:
        print(f"Logging failed: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()

# def add_file_to_vault(user_id, source_path, filename=None):
#     """Complete workflow: Encrypt file + store in DB"""
#     if filename is None:
#         filename = os.path.basename(source_path)
#
#     # Get or generate encryption key
#     key = get_user_encryption_key(user_id)
#     if not key:
#         key = _file_storage._generate_aes_key()
#         update_user_encryption_key(user_id, key)
#
#     # Encrypt and store file
#     encrypted_path = _file_storage.encrypt_file(source_path, key)
#
#     # Add to database
#     return add_file_to_db(user_id, filename, encrypted_path)
#
# def open_file_from_vault(file_id, user_id):
#     """Complete workflow: Decrypt file + open temporarily"""
#     # Verify file access
#     file_record = get_file_from_db(file_id, user_id)
#     if not file_record:
#         raise ValueError("File not found or access denied")
#
#     # Get decryption key
#     key = get_user_encryption_key(user_id)
#     if not key:
#         raise ValueError("Encryption key not found")
#
#     # Decrypt to temp location
#     decrypted_path = _file_storage.decrypt_file(file_record['filepath'], key)
#
#     # Open file and return temp directory for cleanup
#     return _file_storage.open_decrypted_file(decrypted_path)
#
# def delete_file_from_vault(file_id, user_id):
#     """Complete workflow: Delete file from storage + DB"""
#     # Verify file exists and belongs to user
#     file_record = get_file_from_db(file_id, user_id)
#     if not file_record:
#         raise ValueError("File not found or access denied")
#
#     # Delete encrypted file
#     _file_storage.delete_encrypted_file(file_record['filepath'])
#
#     # Remove DB record
#     delete_file_from_db(file_id, user_id)