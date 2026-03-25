from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.model.model import EpisodeSchema
from src.service.modelPrediction import perform_calculations
router = APIRouter(prefix="/api", tags=["lightning"])




@router.post("/predict")
async def predict(episode: EpisodeSchema):
    try:
        perform_calculations(episode)
        result = 0
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))