import pandas as pd
import io, uuid
from typing import Optional, Tuple
from storage.db import DB

def read_usage_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    if not {"timestamp","kwh"}.issubset(df.columns):
        raise ValueError("usage csv must have columns: timestamp,kwh")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.sort_values("timestamp")
    return df

def read_tariff_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    if not {"timestamp","price_per_kwh"}.issubset(df.columns):
        raise ValueError("tariff csv must have: timestamp,price_per_kwh (GBP)")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df

def read_carbon_csv(content: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(content))
    if not {"timestamp","g_per_kwh"}.issubset(df.columns):
        raise ValueError("carbon csv must have: timestamp,g_per_kwh")
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df

def persist_session(db: DB, usage_df, tariffs_df=None, carbon_df=None) -> str:
    session_id = str(uuid.uuid4())
    db.save_df(session_id, "usage", usage_df)
    if tariffs_df is not None:
        db.save_df(session_id, "tariffs", tariffs_df)
    if carbon_df is not None:
        db.save_df(session_id, "carbon", carbon_df)
    return session_id

def load_session(db: DB, session_id: str) -> Tuple[pd.DataFrame, Optional[pd.DataFrame], Optional[pd.DataFrame]]:
    return db.load_df(session_id, "usage"), db.load_df(session_id, "tariffs"), db.load_df(session_id, "carbon")