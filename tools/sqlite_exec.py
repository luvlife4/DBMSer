import sqlite3

_conn = None

def _get_conn():
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(":memory:")
        _conn.row_factory = sqlite3.Row
    return _conn


def exec_sql(sql: str) -> dict:
    try:
        conn = _get_conn()
        cur = conn.execute(sql)
        upper = sql.strip().upper()
        if upper.startswith("SELECT") or upper.startswith("PRAGMA"):
            rows = [dict(r) for r in cur.fetchall()]
            cols = [d[0] for d in cur.description]
            return {"ok": True, "columns": cols, "rows": rows}
        else:
            conn.commit()
            return {"ok": True, "affected_rows": cur.rowcount}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def show_schema() -> dict:
    try:
        conn = _get_conn()
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        tables = [r[0] for r in cur.fetchall()]
        if not tables:
            return {"ok": True, "tables": [], "schema_text": "（当前数据库中没有表）"}
        parts = []
        for t in tables:
            cur = conn.execute(f"PRAGMA table_info('{t}')")
            cols = cur.fetchall()
            col_str = ", ".join(f"{c[1]} {c[2]}" for c in cols)
            parts.append(f"{t}({col_str})")
        return {"ok": True, "tables": tables, "schema_text": "; ".join(parts)}
    except Exception as e:
        return {"ok": False, "error": str(e)}
