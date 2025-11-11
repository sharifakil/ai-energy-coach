import pandas as pd

def join_carbon(usage: pd.DataFrame, carbon: pd.DataFrame) -> pd.DataFrame:
    u = usage.copy()
    c = carbon.copy().set_index("timestamp").sort_index()
    u = u.join(c["g_per_kwh"], on="timestamp", how="left")
    u["g_per_kwh"] = u["g_per_kwh"].ffill().bfill()
    return u