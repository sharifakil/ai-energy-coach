from fastapi import UploadFile, File, HTTPException, Depends
import pandas as pd
from io import StringIO
import uuid

@app.post("/upload")
async def upload(
    usage_csv: UploadFile = File(...),
    tariffs_csv: UploadFile | None = File(None),
    carbon_csv: UploadFile | None = File(None),
    db = Depends(get_db),
):
    session_id = str(uuid.uuid4())

    # ---- Usage (required)
    try:
        usage_df = pd.read_csv(StringIO((await usage_csv.read()).decode("utf-8")))
        usage_df.columns = [c.strip().lower() for c in usage_df.columns]
        if not {"timestamp", "kwh"} <= set(usage_df.columns):
            raise ValueError("usage csv must have: timestamp,kwh")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid usage CSV: {e}")

    # ---- Tariffs (optional)
    tariffs_df = None
    if tariffs_csv is not None:
        try:
            tariffs_df = pd.read_csv(StringIO((await tariffs_csv.read()).decode("utf-8")))
            tariffs_df.columns = [c.strip().lower() for c in tariffs_df.columns]
            if not {"timestamp", "price_per_kwh"} <= set(tariffs_df.columns):
                raise ValueError("tariff csv must have: timestamp,price_per_kwh (GBP)")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid tariff CSV: {e}")

    # ---- Carbon (optional)
    carbon_df = None
    if carbon_csv is not None:
        try:
            carbon_df = pd.read_csv(StringIO((await carbon_csv.read()).decode("utf-8")))
            carbon_df.columns = [c.strip().lower() for c in carbon_df.columns]
            if not {"timestamp", "g_per_kwh"} <= set(carbon_df.columns):
                raise ValueError("carbon csv must have: timestamp,g_per_kwh")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid carbon CSV: {e}")

    # Persist and return
    ingest.save_session(db, session_id, usage_df, tariffs_df, carbon_df)
    return {"session_id": session_id}
