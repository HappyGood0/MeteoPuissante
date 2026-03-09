function CsvImport() {
  function handleFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    alert(`Import CSV placeholder: ${file.name}`);
  }

  return (
    <div className="card">
      <h3>Import CSV</h3>
      <p className="muted">
        PLACEHOLDER, IMPLEMENTER L IMPORT!!
      </p>
      <input type="file" accept=".csv" onChange={handleFileChange} />
    </div>
  );
}

export default CsvImport;