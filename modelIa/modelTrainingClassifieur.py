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

csv_path = "../bdd/segment_alerts_all_airports_train.csv"
data = pd.read_csv(csv_path, sep=",")

date_cols = ['date']
string_cols = ['airport', 'icloud']  # colonnes catégorielles
numeric_cols = ['lon', 'lat', 'amplitude', 'maxis', 'dist', 'azimuth']

# Préparer les features
def preprocess(df):
    df = df.copy()
    # Extraire des features utiles depuis la date
    df['date'] = pd.to_datetime(df['date'])
    df['hour']      = df['date'].dt.hour
    df['month']     = df['date'].dt.month
    df['dayofweek'] = df['date'].dt.dayofweek

    return df

x = preprocess(data.iloc[:, :-1])
y = data['is_last_lightning_cloud_ground']

# Encoder les colonnes string
string_cols_remaining = ['airport', 'icloud']

preprocessor = ColumnTransformer(transformers=[
    ('cat', OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1), 
     string_cols_remaining)
], remainder='passthrough')  # laisse passer les numériques tels quels

model = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('clf', HistGradientBoostingClassifier(
        max_iter=200,
        max_depth=10,
        random_state=42
    ))
])

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
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

joblib.dump(model, 'model.pkl')




# y = data['is_last_lightning_cloud_ground']
# x = data.iloc[:, :-1]
# # split 80% train / 20% test ; retirer la première ligne demandée uniquement du train

# y_train, y_test = train_test_split(y, test_size=0.2, random_state=42)
# x_train, x_test = train_test_split(x, test_size=0.2, random_state=42)

# params = {"n_estimators": 100, "max_depth": 50, "min_samples_split": 2, "random_state": 42}

# model = Pipeline(
#     steps=[
#         ("imputer", SimpleImputer(strategy="median")),
#         ("scaler", StandardScaler()),
#         ("reg", RandomForestClassifier(**params)),
#    ]
# )
# model.fit(x_train, y_train)