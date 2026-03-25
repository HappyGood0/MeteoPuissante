from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from src.model.model import EpisodeSchema
from src.service.modelPrediction import perform_calculations_input, perform_calculations_csv
import pandas as pd
from io import StringIO

router = APIRouter(prefix="/api", tags=["lightning"])

REQUIRED_COLUMNS = {"date", "lat", "lon", "amplitude", "icloud"}


@router.post("/import-csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Le fichier doit être un CSV.")

    content = await file.read()
    try:
        df = pd.read_csv(StringIO(content.decode("utf-8")))
        result = perform_calculations_csv(df)
    except Exception:
        raise HTTPException(status_code=400, detail="Impossible de lire le fichier CSV.")

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"Colonnes manquantes : {', '.join(sorted(missing))}",
        )

    return result




@router.post("/predict")
async def predict(episode: EpisodeSchema):
    try:
        result = perform_calculations_input(episode)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))