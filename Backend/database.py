import mysql.connector

from backend.config import Config


def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )


def db_execute(query, params=(), fetch=False, commit=True):
    """Safely executes a database query with transaction handling."""

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(query, params)

        if fetch:
            return cursor.fetchall()

        if commit:
            conn.commit()

        return cursor.lastrowid

    except Exception:
        conn.rollback()
        raise

    finally:
        cursor.close()
        conn.close()