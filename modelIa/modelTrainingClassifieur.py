from pathlib import Path
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, f1_score, precision_recall_curve
)

# ── Chargement ───────────────────────────────────────────────────────────────
print("📊 Chargement bdd eclairs")
data = pd.read_csv("bdd/segment_alerts_Biarritz_train_clean.csv", sep=",")

TARGET = "is_last_lightning_cloud_ground"
DROP_COLS = ["airport_alert_id"]
data = data.drop(columns=[c for c in DROP_COLS if c in data.columns])

# ── Split temporel ───────────────────────────────────────────────────────────
train_size = int(len(data) * 0.8)
x_train = data.drop(columns=[TARGET]).iloc[:train_size]
y_train = data[TARGET].iloc[:train_size]
x_test  = data.drop(columns=[TARGET]).iloc[train_size:]
y_test  = data[TARGET].iloc[train_size:]

# Calcul du ratio réel de déséquilibre
n_false = (y_train == False).sum()
n_true  = (y_train == True).sum()
ratio   = n_false / n_true

print(f"Ratio déséquilibre : {ratio:.0f}x  ({n_true} True / {n_false} False)")

# ── Modèle avec poids manuel ─────────────────────────────────────────────────
# On donne un poids = ratio réel à la classe True pour compenser
params = {
    "n_estimators": 300,
    "max_depth": 15,
    "min_samples_split": 10,
    "class_weight": {False: 1, True: ratio},  
    "random_state": 42,
    "n_jobs": -1,
}

model = Pipeline(steps=[
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler",  StandardScaler()),
    ("clf",     RandomForestClassifier(**params)),
])

model.fit(x_train, y_train)
predictions_proba = model.predict_proba(x_test)[:, 1]

# ── Recherche du meilleur seuil ──────────────────────────────────────────────
precisions, recalls, thresholds = precision_recall_curve(y_test, predictions_proba)
f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-9)
best_idx       = f1_scores.argmax()
best_threshold = thresholds[best_idx]

correction       = ratio / (ratio + 100) * 0.2  # asymptote à +0.2, jamais atteinte
threshold_ajuste = min(best_threshold + correction, 0.90)  # ne pas dépasser 0.90 pour éviter de trop pénaliser

print(f"\n🎯 Meilleur seuil trouvé : {best_threshold:.3f}")
print(f"   → Seuil ajusté (correction) : {threshold_ajuste:.3f}")
print(f"   → Précision : {precisions[best_idx]:.3f}")
print(f"   → Rappel    : {recalls[best_idx]:.3f}")
print(f"   → F1        : {f1_scores[best_idx]:.3f}")

# ── Prédictions avec seuil optimisé ─────────────────────────────────────────
predictions_tuned = (predictions_proba >= best_threshold)

predictions_ajustees = (predictions_proba >= threshold_ajuste)
print("\n📈 Rapport de classification AVANT ajustement :")
print(classification_report(y_test, predictions_tuned, digits=3))
print(f"✅ ROC-AUC : {roc_auc_score(y_test, predictions_proba):.4f}")
print("\n🔢 Matrice de confusion :")
print(confusion_matrix(y_test, predictions_tuned))

print("\n📈 Rapport de classification APRÈS ajustement :")
print(classification_report(y_test, predictions_ajustees, digits=3))
print(f"✅ ROC-AUC : {roc_auc_score(y_test, predictions_proba):.4f}")
print("\n🔢 Matrice de confusion :")
print(confusion_matrix(y_test, predictions_ajustees))


# # ── Courbe Précision / Rappel ────────────────────────────────────────────────
# plt.figure(figsize=(8, 5))
# plt.plot(recalls, precisions, lw=2, label="Courbe Précision-Rappel")
# plt.scatter(recalls[best_idx], precisions[best_idx],
#             color="red", zorder=5, label=f"Seuil optimal ({best_threshold:.2f})")
# plt.xlabel("Rappel (Recall)")
# plt.ylabel("Précision")
# plt.title("Courbe Précision-Rappel — dernier éclair")
# plt.legend()
# plt.tight_layout()
# plt.savefig("./StockageModels/precision_recall.png")
# plt.show()

#features : 
print("\n🔍 Importance des features :")
feature_names = x_train.columns.tolist()
importances = model.named_steps["clf"].feature_importances_
feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)
print("\n🌟 Top  features :")
print(feat_imp)

# ── Sauvegarde du modèle ET du seuil ────────────────────────────────────────
Path("./StockageModels").mkdir(exist_ok=True)
joblib.dump({"model": model, "threshold": threshold_ajuste},
            "./StockageModels/modelNantes.pkl")
print(f"\n💾 Modèle + seuil ({threshold_ajuste:.3f}) sauvegardés.")