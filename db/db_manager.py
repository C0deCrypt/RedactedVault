import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Initialize connection
_connection = None

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

def get_files_for_user(user_id):
    """List files for a user"""
    conn = get_connection()
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

def log_access(user_id, event_type, details=None):
    """Record access attempts"""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO vault_access_logs 
            (user_id, event_type, details)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_id, event_type, details))
        conn.commit()
    except Error as e:
        print(f"Logging failed: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()