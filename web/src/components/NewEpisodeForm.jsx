
import { useState } from "react";
import LightningInput from "./LightningInput";
import CsvImport from "./CsvImport";

function NewEpisodeForm({ onCreateEpisode, onCancel }) {
  const [airport, setAirport] = useState("Pau");

  function handleFirstEventSubmit(firstEvent) {
    onCreateEpisode({
      airport,
      firstEvent
    });
  }

  return (
    <section className="layout-two-columns">
      <div className="card">
        <h2>Nouvel épisode</h2>

        <label>
          Aéroport
          <select value={airport} onChange={(e) => setAirport(e.target.value)}>
            <option value="Pau">Pau</option>
            <option value="Biarritz">Biarritz</option>
            <option value="Toulouse">Toulouse</option>
          </select>
        </label>

        <div className="actions">
          <button className="secondary" onClick={onCancel}>
            Retour
          </button>
        </div>
      </div>

      <LightningInput
        onSubmit={handleFirstEventSubmit}
        submitLabel="Créer l’épisode avec ce premier éclair"
      />

      <CsvImport />
    </section>
  );
}

export default NewEpisodeForm;