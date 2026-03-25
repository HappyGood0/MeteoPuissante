import { useState } from "react";
import { importCsv } from "../utils/api";

function CsvImport() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  async function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStatus(null);
    try {
      const result = await importCsv(file);
      setStatus({ ok: true, rows: result.rows, columns: result.columns });
    } catch (err) {
      setStatus({ ok: false, error: err.message });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      <h3>Import CSV</h3>
      <input type="file" accept=".csv" onChange={handleFileChange} disabled={loading} />
      {loading && <p className="muted">Envoi en cours...</p>}
      {status?.ok && (
        <p style={{ color: "green" }}>
          {status.rows} lignes importées ({status.columns.length} colonnes)
        </p>
      )}
      {status && !status.ok && (
        <p style={{ color: "red" }}>{status.error}</p>
      )}
    </div>
  );
}

export default CsvImport;