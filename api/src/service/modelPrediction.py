from src.model.model import EpisodeSchema
import joblib
import pandas as pd
from src.service.cleanData import process_data


def perform_calculations(data: EpisodeSchema):
    airport=data.airport
    MODEL_PATH = f"StockageModels/model{airport}.pkl"
    print(MODEL_PATH)
    checkpoint = joblib.load(MODEL_PATH)
    model = checkpoint['model']
    threshold = checkpoint['threshold']
    airport=data.airport
    liste_dicts = [{**event.model_dump(), "lightning_id": 0, "lightning_airport_id": 0, "azimuth":4, "dist":4, "airport":airport, "is_last_lightning_cloud_ground":False, "airport_alert_id":0} for event in data.events]
    print(airport)

    df = pd.DataFrame(liste_dicts)
    df = process_data(df)
    print(type(df))

 

    df = df[model.feature_names_in_]


    predict = model.predict(df)
    print(predict)
    return {"result": predict}
