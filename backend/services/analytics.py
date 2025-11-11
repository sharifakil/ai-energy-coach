import pandas as pd
import numpy as np

def prepare(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df = df.set_index("timestamp").sort_index()
    # infer cadence (30-min smart meters common in UK). Normalize to hourly kWh
    # if interval < 60min, scale to hourly-equivalent for reporting
    diffs = df.index.to_series().diff().dropna()
    minutes = int(diffs.mode().iloc[0].total_seconds() // 60)
    df["kwh_normalized"] = df["kwh"] * (60 / minutes)
    df["hour"] = df.index.hour
    df["dow"]  = df.index.dayofweek
    return df

def compute_baseload_kw(df: pd.DataFrame) -> float:
    # Baseload ~ 10th percentile of hourly kW (kWh since normalized hourly)
    hourly = df["kwh_normalized"].resample("1H").sum()
    return float(np.percentile(hourly.values, 10))

def detect_peak_windows(df: pd.DataFrame, top_n: int = 3):
    hourly = df["kwh_normalized"].resample("1H").sum()
    hourly_mean = hourly.groupby(hourly.index.hour).mean()
    top_hours = hourly_mean.sort_values(ascending=False).head(top_n)
    windows = []
    for h in top_hours.index:
        windows.append({
            "start": f"{h:02d}:00",
            "end": f"{(h+1)%24:02d}:00",
            "avg_kwh": float(top_hours.loc[h])
        })
    top_hour = int(hourly_mean.idxmax())
    return windows, top_hour

def estimate_monthly_bill(df: pd.DataFrame) -> float:
    if "price_per_kwh" not in df.columns:
        return None
    hourly = df["kwh_normalized"].resample("1H").sum()
    price = df["price_per_kwh"].resample("1H").ffill().reindex(hourly.index).fillna(method="bfill")
    cost_series = hourly * price
    # scale to 30 days if data shorter
    days = (hourly.index[-1] - hourly.index[0]).days + 1
    scale = 30 / max(days, 1)
    return float(cost_series.sum() * scale)

def compute_features(df: pd.DataFrame):
    baseload = compute_baseload_kw(df)
    peaks, top_hour = detect_peak_windows(df)
    return {"baseload_kw": baseload, "peak_windows": peaks, "top_peak_hour": top_hour}

def summarize(df: pd.DataFrame, feats: dict):
    resp = {
        "daily_kwh": float(df["kwh"].resample("1D").sum().mean()),
        "baseload_kw": float(feats["baseload_kw"]),
        "peak_windows": feats["peak_windows"],
        "top_peak_hour": feats["top_peak_hour"],
    }
    if "price_per_kwh" in df.columns:
        hourly_price = df["price_per_kwh"].resample("1H").mean()
        resp["tariff_spread_p_per_kwh"] = float((hourly_price.max() - hourly_price.min())*100)
        resp["est_monthly_bill"] = estimate_monthly_bill(df)
    if "g_per_kwh" in df.columns:
        hourly = df["kwh_normalized"].resample("1H").sum()
        carbon = df["g_per_kwh"].resample("1H").ffill().reindex(hourly.index).fillna(method="bfill")
        resp["carbon_intensity_avg"] = float((carbon*hourly).sum() / max(hourly.sum(), 1e-6))
    return resp

def load_factor(df: pd.DataFrame) -> float:
    hourly = df["kwh_normalized"].resample("1H").sum()
    avg_kw = hourly.mean()
    peak_kw = hourly.max() or 1e-6
    return float(avg_kw / peak_kw)

def weekday_weekend_split(df: pd.DataFrame):
    hourly = df["kwh_normalized"].resample("1H").sum()
    wd = hourly[hourly.index.dayofweek < 5].sum()
    we = hourly[hourly.index.dayofweek >= 5].sum()
    total = max(wd + we, 1e-6)
    return float(wd/total), float(we/total)
