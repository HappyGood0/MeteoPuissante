from typing import List, Optional
from pydantic import BaseModel



class LightningEvent(BaseModel):
    date: str
    lat: float
    lon: float
    amplitude: float
    maxis: Optional[float] = None
    icloud: bool

# Modèle pour l'épisode complet envoyé par App.jsx
class EpisodeSchema(BaseModel):
    id: str
    airport: str
    startedAt: str
    status: str
    events: List[LightningEvent]
    prediction: Optional[dict] = None