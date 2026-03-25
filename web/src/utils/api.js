

export async function checkApiHealth() {
  try {
    const response = await fetch("/api/health");
    if (!response.ok) {
      throw new Error("API indisponible");
    }

    return { ok: true };
  } catch (error) {
    return { ok: false, error: error.message };
  }
}

export async function predictEpisode(episode) {
  try {
    const response = await fetch("http://localhost:8000/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(episode)
    });

    if (!response.ok) {
      throw new Error("Endpoint /api/predict indisponible");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    return {
      probability_last: null,
      recommendation: "unknown",
      message: "Prédiction non disponible pour le moment"
    };
  }
}

export async function importCsv(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/import-csv", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Erreur lors de l'import.");
  }
  return data;
}