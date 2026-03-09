
function PredictionPanel({ prediction }) {
  const probability =
    prediction?.probability_last === null || prediction?.probability_last === undefined
      ? "--"
      : `${Math.round(prediction.probability_last * 100)} %`;

  const recommendation = prediction?.recommendation ?? "unknown";
  const message = prediction?.message ?? "Pas de prédiction disponible.";

  return (
    <div className="card">
      <h3>Prédiction / résultat</h3>

      <p>
        <span className="label">Probabilité que l’épisode soit terminé :</span>{" "}
        {probability}
      </p>

      <p>
        <span className="label">Recommandation :</span> {recommendation}
      </p>

      <p>
        <span className="label">Message :</span> {message}
      </p>
    </div>
  );
}

export default PredictionPanel;