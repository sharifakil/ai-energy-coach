from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class PeakWindow(BaseModel):
    start: str
    end: str
    avg_kwh: float

class AnalyzeResponse(BaseModel):
    session_id: str
    daily_kwh: float
    baseload_kw: float
    peak_windows: List[PeakWindow]
    top_peak_hour: int
    tariff_spread_p_per_kwh: Optional[float] = None
    est_monthly_bill: Optional[float] = None
    carbon_intensity_avg: Optional[float] = None
    load_factor: Optional[float] = None
    weekday_ratio: Optional[float] = None
    weekend_ratio: Optional[float] = None

class Tip(BaseModel):
    title: str
    detail: str
    est_savings_per_month_gbp: Optional[float] = None
    est_co2_saving_kg_per_month: Optional[float] = None
    evidence: Dict[str, Any] = {}

class RecommendResponse(BaseModel):
    session_id: str
    recommendations: List[Tip]
