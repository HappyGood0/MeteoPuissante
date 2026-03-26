import { useState } from "react";

function CsvImport({ onImportEvents }) {
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);

  function parseValue(value) {
    if (value === undefined || value === null) return "";
    return String(value).trim();
  }

  function parseBoolean(value) {
    const normalized = parseValue(value).toLowerCase();
    return normalized === "true" || normalized === "1";
  }

  function parseCsvText(text) {
    const lines = text
      .split(/\r?\n/)
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    if (lines.length < 2) {
      throw new Error("Le CSV est vide ou ne contient pas de données.");
    }

    const headers = lines[0].split(",").map((h) => h.trim());

    const required = ["date", "dist", "azimuth", "amplitude", "icloud"];
    const missing = required.filter((col) => !headers.includes(col));

    if (missing.length > 0) {
      throw new Error(`Colonnes manquantes : ${missing.join(", ")}`);
    }

    const events = lines.slice(1).map((line, index) => {
      const values = line.split(",").map((v) => v.trim());
      const row = Object.fromEntries(headers.map((h, i) => [h, values[i] ?? ""]));

      return {
        date: parseValue(row.date),
        dist: Number(row.dist),
        azimuth: Number(row.azimuth),
        amplitude: Number(row.amplitude),
        maxis: parseValue(row.maxis) === "" ? null : Number(row.maxis),
        icloud: parseBoolean(row.icloud),
      };
    });

    return events;
  }

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStatus(null);

    try {
      const text = await file.text();
      const events = parseCsvText(text);

      if (!events.length) {
        throw new Error("Aucun éclair valide trouvé dans le fichier.");
      }

      onImportEvents(events);
      setStatus({ ok: true, count: events.length });
    } catch (err) {
      setStatus({ ok: false, error: err.message });
    } finally {
      setLoading(false);
      event.target.value = "";
    }
  }

  return (
    <div className="card">
      <h3>Import CSV</h3>
      <input type="file" accept=".csv" onChange={handleFileChange} disabled={loading} />

      {loading && <p className="muted">Lecture du fichier...</p>}

      {status?.ok && (
        <p style={{ color: "green" }}>
          {status.count} éclair(s) importé(s) dans l’épisode.
        </p>
      )}

      {status && !status.ok && (
        <p style={{ color: "red" }}>{status.error}</p>
      )}
    </div>
  );
}

export default CsvImport;