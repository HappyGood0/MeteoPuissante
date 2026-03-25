from pathlib import Path
import joblib
import pandas as pd
import numpy as np
from xgboost import XGBClassifier
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, f1_score, precision_recall_curve
)

villes = ["Biarritz","Ajaccio","Nantes","Bastia","Pise"]

for ville in villes:


# ── Chargement ───────────────────────────────────────────────────────────────
    print("📊 Chargement bdd eclairs " + ville)
    data = pd.read_csv("bdd/segment_alerts_"+ ville + "_train_clean.csv", sep=",")

    TARGET = "is_last_lightning_cloud_ground"
    DROP_COLS = ["UV_INDICE"]
    data = data.drop(columns=[c for c in DROP_COLS if c in data.columns])

    # ── Split temporel ───────────────────────────────────────────────────────────
    train_size = int(len(data) * 0.8)
    x_train = data.drop(columns=[TARGET]).iloc[:train_size]
    y_train = data[TARGET].iloc[:train_size]
    x_test  = data.drop(columns=[TARGET]).iloc[train_size:]
    y_test  = data[TARGET].iloc[train_size:]
    # Supprimer les colonnes qui n'ont qu'une seule valeur unique (constantes)
    cols_constantes = [col for col in x_train.columns if x_train[col].nunique() <= 1]
    if cols_constantes:
        print(f"⚠️ Suppression des colonnes constantes : {cols_constantes}")
        x_train = x_train.drop(columns=cols_constantes)
        x_test = x_test.drop(columns=cols_constantes)
    # Calcul du ratio réel de déséquilibre
    n_false = (y_train == False).sum()
    n_false_test = (y_test == False).sum()
    n_true  = (y_train == True).sum()
    n_true_test  = (y_test == True).sum()
    ratio   = n_false / n_true

    print(f"Ratio déséquilibre : {ratio:.0f}x  ({n_true} True / {n_false} False)")
    print(f"Nombre vrai a trouver : {n_true_test}")
    print(f"Nombre faux a éviter : {n_false_test}")
    # ── Modèle avec poids manuel ─────────────────────────────────────────────────
    # On donne un poids = ratio réel à la classe True pour compenser
    params_xgb = {
        "n_estimators": 500,       # Plus d'arbres, car le boosting est itératif
        "max_depth": 6,            # On réduit la profondeur (XGB est plus sensible au surapprentissage)
        "learning_rate": 0.05,     # Vitesse d'apprentissage (pas trop élevé)
        "scale_pos_weight": ratio, # Gère le déséquilibre des classes
        "random_state": 42,
        "tree_method": "hist",     # Accélère l'entraînement
        "n_jobs": -1,
        "eval_metric": "logloss"
    }

    model = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler",  StandardScaler()),
        ("clf",     XGBClassifier(**params_xgb)),
    ])

    model.fit(x_train, y_train.astype(int))
    predictions_proba = model.predict_proba(x_test)[:, 1]

    # ── Recherche du meilleur seuil ──────────────────────────────────────────────
    precisions, recalls, thresholds = precision_recall_curve(y_test, predictions_proba)
    f1_scores = 2 * (precisions * recalls) / (precisions + recalls + 1e-9)
    best_idx       = f1_scores.argmax()
    best_threshold = thresholds[best_idx]

    correction       = ratio / (ratio + 100) * 0.15  # asymptote à +0.2, jamais atteinte
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

    # On récupère le classifieur final de la pipeline
    clf = model.named_steps["clf"]

    # XGBoost stocke les noms des features qu'il a utilisé pour l'entraînement ici :
    if hasattr(clf, "feature_names_in_"):
        feature_names = clf.feature_names_in_
    else:
        # Si non disponible, on reprend x_train mais on filtre les colonnes
        feature_names = x_train.columns.tolist()

    importances = clf.feature_importances_

    # Création de la série avec les noms validés par le modèle
    feat_imp = pd.Series(importances, index=feature_names).sort_values(ascending=False)

    print("\n🌟 Top features :")
    print(feat_imp.head(15))

    # ── Sauvegarde du modèle ET du seuil ────────────────────────────────────────
    Path("./StockageModels").mkdir(exist_ok=True)
    joblib.dump({"model": model, "threshold": threshold_ajuste},
                "./StockageModels/model" + ville + ".pkl")
    print(f"\n💾 Modèle de " + ville + " sauvegardés avec succès")