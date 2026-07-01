import os
import sqlite3

# Path to the database — always relative to this file's location
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "retail.db")

def get_connection():
    """Returns a connection with dict-style row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn