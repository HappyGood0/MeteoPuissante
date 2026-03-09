
import LightningInput from "./LightningInput";
import EpisodeHistory from "./EpisodeHistory";
import PredictionPanel from "./PredictionPanel";
import CsvImport from "./CsvImport";

function CurrentEpisodeView({
  episode,
  onAddEvent,
  onResetEpisode,
  onStartNew
}) {
  return (
    <section className="current-episode-layout">
      <div className="card">
        <h2>Épisode en cours</h2>
        <p>
          <span className="label">Aéroport :</span> {episode.airport}
        </p>
        <p>
          <span className="label">Début :</span> {episode.startedAt}
        </p>
        <p>
          <span className="label">Nombre d’éclairs :</span> {episode.events.length}
        </p>

        <div className="actions">
          <button className="danger" onClick={onResetEpisode}>
            Supprimer l’épisode courant
          </button>
          <button className="secondary" onClick={onStartNew}>
            Démarrer un nouvel épisode
          </button>
        </div>
      </div>

      <div className="grid-two">
        <LightningInput onSubmit={onAddEvent} />
        <CsvImport />
      </div>

      <div className="grid-two">
        <EpisodeHistory events={episode.events} />
        <PredictionPanel prediction={episode.prediction} />
      </div>
    </section>
  );
}

export default CurrentEpisodeView;