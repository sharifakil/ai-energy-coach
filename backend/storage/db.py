import sqlite3, json, os, pandas as pd
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "coach.db")

def _init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS datasets (
        session_id TEXT NOT NULL,
        kind TEXT NOT NULL,            -- 'usage' | 'tariffs' | 'carbon'
        data_json TEXT NOT NULL,
        PRIMARY KEY (session_id, kind)
    )""")
    con.commit()
    con.close()
_init()

class DB:
    def save_df(self, session_id: str, name: str, df: pd.DataFrame):
        con = sqlite3.connect(DB_PATH)
        con.execute("REPLACE INTO datasets(session_id, kind, data_json) VALUES (?,?,?)",
                    (session_id, name, df.to_json(orient="table", date_format="iso")))
        con.commit(); con.close()

    def load_df(self, session_id: str, name: str) -> Optional[pd.DataFrame]:
        con = sqlite3.connect(DB_PATH)
        cur = con.execute("SELECT data_json FROM datasets WHERE session_id=? AND kind=?", (session_id, name))
        row = cur.fetchone()
        con.close()
        if not row: return None
        df = pd.read_json(row[0], orient="table")
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        return df

_db = DB()
def get_db(): return _db
