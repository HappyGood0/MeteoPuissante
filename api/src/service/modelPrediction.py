from src.model.model import EpisodeSchema
import joblib


MODEL_PATH = "StockageModels/modelNantes.pkl"
model = joblib.load(MODEL_PATH)

def perform_calculations(data: EpisodeSchema):
    print(data.events[0])
    data
    return {"score": 0.85, "label": "Orage violent", "suggestion": "Alerte orange"}
