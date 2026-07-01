import sqlite3
from core.database import DB_PATH

MAX_ROWS = 50
DISALLOWED = ("insert", "update", "delete", "drop", "alter", "create", "replace")

def _get_connection():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_schema() -> dict:
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row["name"] for row in cursor.fetchall()]
        schema = {}
        for table in tables:
            cursor.execute(f"PRAGMA table_info({table})")
            schema[table] = [{"column": row["name"], "type": row["type"]} for row in cursor.fetchall()]
        conn.close()
        return {"success": True, "schema": schema}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_sql(query: str) -> dict:
    normalized = query.strip().lower()
    if any(normalized.startswith(kw) for kw in DISALLOWED):
        return {"success": False, "error": f"Only SELECT statements allowed."}
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute(query)
        raw_rows = cursor.fetchmany(MAX_ROWS + 1)
        truncated = len(raw_rows) > MAX_ROWS
        rows = [dict(row) for row in raw_rows[:MAX_ROWS]]
        conn.close()
        return {"success": True, "rows": rows, "row_count": len(rows), "truncated": truncated}
    except sqlite3.OperationalError as e:
        return {"success": False, "error": f"SQL error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}