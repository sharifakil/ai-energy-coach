import pandas as pd
from typing import List, Dict, Any
import numpy as np

def _money_and_co2(shift_kwh: float, price_peak: float, price_off: float, carbon_peak: float = None, carbon_off: float = None):
    gbp = max((price_peak - price_off), 0) * shift_kwh * 30  # monthly
    co2 = None
    if carbon_peak is not None and carbon_off is not None:
        co2 = max((carbon_peak - carbon_off), 0) * shift_kwh * 30 / 1000.0  # g->kg
    return gbp, co2

def generate_recommendations(df: pd.DataFrame) -> List[Dict[str, Any]]:
    tips = []
    hourly = df["kwh_normalized"].resample("1H").sum()
    hour_mean = hourly.groupby(hourly.index.hour).mean()

    # 1) Peak shifting if tariffs present
    if "price_per_kwh" in df.columns:
        price_hour = df["price_per_kwh"].resample("1H").mean().groupby(lambda ts: ts.hour).mean()
        peak_h = int(price_hour.idxmax())
        off_h  = int(price_hour.idxmin())
        peak_load = float(hour_mean.loc[peak_h])
        shiftable = 0.35 * peak_load  # assume 35% shiftable loads for MVP
        gbp, co2 = _money_and_co2(
            shiftable, price_hour.loc[peak_h], price_hour.loc[off_h],
            df["g_per_kwh"].mean() if "g_per_kwh" in df.columns else None,
            df["g_per_kwh"].mean() if "g_per_kwh" in df.columns else None
        )
        tips.append({
            "title": f"Shift ~{shiftable:.2f} kWh from {peak_h:02d}:00 → {off_h:02d}:00",
            "detail": "Schedule dishwasher, laundry, EV/top-up to off-peak window. Use timers or smart plugs.",
            "est_savings_per_month_gbp": round(gbp, 2) if gbp else None,
            "est_co2_saving_kg_per_month": round(co2, 2) if co2 else None,
            "evidence": {"peak_hour": peak_h, "off_peak_hour": off_h, "assumed_shiftable_fraction": 0.35}
        })

    # 2) Baseload reduction
    baseload = float(np.percentile(hourly.values, 10))
    if baseload > 0.15:  # kW threshold for “high” baseload (tune later)
        reduce_kw = 0.05  # target 50W reduction MVP
        price_avg = float(df.get("price_per_kwh", pd.Series([0.30])).mean())
        gbp = reduce_kw * 24 * 30 * price_avg
        tips.append({
            "title": "Cut always-on (baseload) by ~50 W",
            "detail": "Identify standby drains (routers, set-top boxes, old fridge, chargers). Use smart plug to verify.",
            "est_savings_per_month_gbp": round(gbp, 2),
            "est_co2_saving_kg_per_month": None,
            "evidence": {"baseload_kw": baseload, "target_kw_reduction": reduce_kw}
        })

    # 3) Weekend load move (if weekday peaks)
    weekday = hourly[hourly.index.dayofweek < 5]
    weekend = hourly[hourly.index.dayofweek >= 5]
    if not weekday.empty and not weekend.empty:
        wkday_peak_hour = int(weekday.groupby(weekday.index.hour).mean().idxmax())
        wkend_peak_hour = int(weekend.groupby(weekend.index.hour).mean().idxmax())
        if wkday_peak_hour != wkend_peak_hour:
            tips.append({
                "title": "Batch laundry/dishwasher to weekend off-peak",
                "detail": "If your weekday evenings spike, shift chores to off-peak weekend slots.",
                "est_savings_per_month_gbp": None,
                "est_co2_saving_kg_per_month": None,
                "evidence": {"weekday_peak_hour": wkday_peak_hour, "weekend_peak_hour": wkend_peak_hour}
            })

    # 4) EV-specific (heuristic MVP)
    # If peak around 19–22h and large spikes > 2 kWh, assume EV charging pattern
    if hour_mean.idxmax() in [19,20,21,22] and hour_mean.max() > 2.0:
        tips.append({
            "title": "Enable EV scheduled charging",
            "detail": "Use vehicle/app to charge after midnight to hit cheapest & cleanest grid hours.",
            "evidence": {"peak_hour": int(hour_mean.idxmax()), "avg_kwh_at_peak": float(hour_mean.max())}
        })
    return tips