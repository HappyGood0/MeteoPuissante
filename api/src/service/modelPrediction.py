from src.model.model import EpisodeSchema
import joblib
import pandas as pd
from src.service.cleanData import process_data


def perform_calculations_input(data: EpisodeSchema):
    airport=data.airport
    MODEL_PATH = f"StockageModels/model{airport}.pkl"
    checkpoint = joblib.load(MODEL_PATH)
    model = checkpoint['model']
    threshold = checkpoint['threshold']
    liste_dicts = [{**event.model_dump(), "lightning_id": 0, "lightning_airport_id": 0,"lon":0,"lat":0, "airport":airport, "is_last_lightning_cloud_ground":False, "airport_alert_id":0} for event in data.events]

    df = pd.DataFrame(liste_dicts)
    df = process_data(df)
    print(type(df))

 

    df = df[model.feature_names_in_]


    predict = model.predict(df)
    print("papa")
    print(type(predict))
    print("popo")

    return {"result": predict.tolist()}


def perform_calculations_csv(data: EpisodeSchema):
    airport = data.airport[0]
    MODEL_PATH = f"StockageModels/model{airport}.pkl"
    checkpoint = joblib.load(MODEL_PATH)
    model = checkpoint['model']
    threshold = checkpoint['threshold']
    df = pd.DataFrame(data)
    df = process_data(df)
    print(type(df))

 

    df = df[model.feature_names_in_]


    predict = model.predict(df)
    print("papa")
    print(type(predict))
    print("popo")
    return {"result": predict.tolist()}


