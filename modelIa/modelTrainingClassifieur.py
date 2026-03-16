from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OrdinalEncoder
import pandas as pd

# Configuration MLflow

print("📊 Chargement bdd eclairs")

csv_path = "../bdd/segment_alerts_all_airports_train_clean.csv"
data = pd.read_csv(csv_path, sep=",")

train_size = int(len(data) * 0.8)

y_train = data["is_last_lightning_cloud_ground"].iloc[:train_size]
x_train = data.drop(columns=["is_last_lightning_cloud_ground"]).iloc[:train_size]
y_test = data["is_last_lightning_cloud_ground"].iloc[train_size:]
x_test = data.drop(columns=["is_last_lightning_cloud_ground"]).iloc[train_size:]


params = {"n_estimators": 100, "max_depth": 50, "min_samples_split": 2, "random_state": 42}

model = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("reg", RandomForestClassifier(**params)),
        ]
    )
model.fit(x_train, y_train)
predictions = model.predict(x_test)

metrics = {
    "mse": mean_squared_error(y_test, predictions),
    "mae": mean_absolute_error(y_test, predictions),
    "r2": r2_score(y_test, predictions),
    "train_size": len(x_train),
    "test_size": len(x_test),
}

print(f"✅ MSE: {metrics['mse']:.4f}")
print(f"✅ MAE: {metrics['mae']:.4f}")
print(f"✅ R2: {metrics['r2']:.4f}")

joblib.dump(model, './StockageModels/model.pkl')