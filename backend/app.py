from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import AnalyzeResponse, RecommendResponse
from services import ingest, analytics, tariffs, reco, carbon
from core.deps import get_db
import pandas as pd
from typing import Optional

app = FastAPI(title="AI Energy Coach", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/upload")
async def upload_data(
    usage_csv: UploadFile = File(...),
    tariffs_csv: Optional[UploadFile] = File(None),
    carbon_csv: Optional[UploadFile] = File(None),
    db = Depends(get_db)
):
    try:
        usage_df = ingest.read_usage_csv(await usage_csv.read())
        tariffs_df = ingest.read_tariff_csv(await tariffs_csv.read()) if tariffs_csv else None
        carbon_df = ingest.read_carbon_csv(await carbon_csv.read()) if carbon_csv else None
        # persist minimal session (optional)
        session_id = ingest.persist_session(db, usage_df, tariffs_df, carbon_df)
        return {"session_id": session_id, "rows": len(usage_df)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/analyze", response_model=AnalyzeResponse)
def analyze(session_id: str, db = Depends(get_db)):
    usage_df, tariffs_df, carbon_df = ingest.load_session(db, session_id)
    usage_df = analytics.prepare(usage_df)
    feats = analytics.compute_features(usage_df)

    # join tariffs + carbon if present
    if tariffs_df is not None:
        usage_df = tariffs.join_tariffs(usage_df, tariffs_df)
    if carbon_df is not None:
        usage_df = carbon.join_carbon(usage_df, carbon_df)

    insights = analytics.summarize(usage_df, feats)

    # Build base response
    resp = AnalyzeResponse(session_id=session_id, **insights)

    # Extra KPIs (safe wrapper)
    try:
        from services.analytics import load_factor, weekday_weekend_split
        resp.load_factor = load_factor(usage_df)
        wd, we = weekday_weekend_split(usage_df)
        resp.weekday_ratio, resp.weekend_ratio = wd, we
    except Exception:
        pass

    return resp

@app.get("/recommendations", response_model=RecommendResponse)
def recommendations(session_id: str, db = Depends(get_db)):
    usage_df, tariffs_df, carbon_df = ingest.load_session(db, session_id)
    usage_df = analytics.prepare(usage_df)
    if tariffs_df is not None:
        usage_df = tariffs.join_tariffs(usage_df, tariffs_df)
    if carbon_df is not None:
        usage_df = carbon.join_carbon(usage_df, carbon_df)
    tips = reco.generate_recommendations(usage_df)
    return RecommendResponse(session_id=session_id, recommendations=tips)
