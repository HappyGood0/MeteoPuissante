function PredictionPanel({ prediction }) {
  const results = Array.isArray(prediction?.result) ? prediction.result : [];

  const lastResult = results.length > 0 ? results[results.length - 1] : null;

  const predictionText =
    lastResult === null
      ? "--"
      : Number(lastResult) === 1 || lastResult === true
        ? "Dernier éclair probable"
        : "Pas le dernier éclair";

  return (
    <div className="card">
      <h3>Prédiction / résultat</h3>

      <p>
        <span className="label">Résultat pour le dernier éclair :</span>{" "}
        {predictionText}
      </p>

      <p>
        <span className="label">Sortie brute du modèle :</span>{" "}
        {results.length > 0 ? `[${results.join(", ")}]` : "--"}
      </p>
    </div>
  );
}

export default PredictionPanel;