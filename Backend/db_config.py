from backend.database import get_db_connection, db_execute


def get_connection():
    """Backward-compatible database connection helper."""
    return get_db_connection()


def execute_query(query, params=(), fetch=False):
    """Backward-compatible query helper."""
    return db_execute(
        query,
        params=params,
        fetch=fetch,
        commit=not fetch
    )