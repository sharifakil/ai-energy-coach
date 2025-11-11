import pandas as pd

def join_tariffs(usage: pd.DataFrame, tariffs: pd.DataFrame) -> pd.DataFrame:
    u = usage.copy()
    t = tariffs.copy().set_index("timestamp").sort_index()
    u = u.join(t["price_per_kwh"], on="timestamp", how="left")
    u["price_per_kwh"] = u["price_per_kwh"].ffill().bfill()
    return u