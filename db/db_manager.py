import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Initialize connection and user variables
_connection = None
_current_user = None
_current_user_id = None


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

def get_user_id(username):
    """
    Get the user ID for the given username.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        if cursor:
            cursor.close()


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

def register_user_to_database(username, biometric_type, encrypted_data, unlock_code, encrypted_aes_key):
    """
    Save a new user, their biometric data, unlock code, and encrypted AES key into MySQL.
    """
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # Check if user already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
        else:
            cursor.execute("INSERT INTO users (username) VALUES (%s)", (username,))
            user_id = cursor.lastrowid

        # Save biometric data
        cursor.execute("""
            INSERT INTO biometric_data (user_id, type, data)
            VALUES (%s, %s, %s)
        """, (user_id, biometric_type, encrypted_data))

        # Save vault settings (unlock code + AES key)
        cursor.execute("""
            INSERT INTO vault_settings (user_id, unlock_code, encrypted_aes_key)
            VALUES (%s, %s, %s)
        """, (user_id, unlock_code, encrypted_aes_key))

        conn.commit()

    except Error as e:
        print(f"Error saving user to database: {e}")

    finally:
        if 'cursor' in locals():
            cursor.close()

def get_username_by_unlock_code(unlock_code):
    """
    Retrieve the username associated with a given unlock code.
    Returns None if not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            SELECT u.username
            FROM users u
            JOIN vault_settings v ON u.id = v.user_id
            WHERE v.unlock_code = %s
        """
        cursor.execute(query, (unlock_code,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"DB Error: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()


def fetch_user_biometric(username, biometric_type):
    """
    Fetch encrypted biometric data for a user from the database.
    Returns (user_id, encrypted_data) or (None, None) if not found.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Get user_id
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_result = cursor.fetchone()
        if not user_result:
            return None, None
        user_id = user_result[0]

        # Get biometric data
        cursor.execute("""
            SELECT data FROM biometric_data 
            WHERE user_id = %s AND type = %s
        """, (user_id, biometric_type))
        bio_result = cursor.fetchone()

        if not bio_result:
            return user_id, None

        return user_id, bio_result[0]

    except Error as e:
        print(f"DB error in fetch_user_biometric: {e}")
        return None, None

    finally:
        if 'cursor' in locals():
            cursor.close()

def get_user_unlock_code(username):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT unlock_code
            FROM vault_settings
            WHERE user_id = (
                SELECT id FROM users WHERE username = %s
            )
        """, (username,))
        result = cursor.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"DB error in get_user_unlock_code: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()


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
        cursor.execute("SELECT encrypted_key FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()
        return result['encrypted_key'] if result else None
    finally:
        cursor.close()



def insert_file_record(user_id, original_name, hidden_path):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO files (user_id, filename, filepath)
            VALUES (%s, %s, %s)
        """, (user_id, original_name, hidden_path))
        conn.commit()
    except Error as e:
        print(f"DB error in insert_file_record: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()


def delete_file_record(file_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
        conn.commit()
    except Error as e:
        print(f"DB error in delete_file_record: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()


def get_file_record_by_id(file_id):
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT filename, filepath FROM files
            WHERE id = %s AND user_id = %s
        """, (file_id, get_current_user_id()))
        return cursor.fetchone()
    except Error as e:
        print(f"DB error in get_file_record_by_id: {e}")
        return None
    finally:
        if 'cursor' in locals():
            cursor.close()
