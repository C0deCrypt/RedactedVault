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