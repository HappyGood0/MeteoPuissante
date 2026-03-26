export async function checkApiHealth() {
  try {
    const response = await fetch("http://localhost:8000/health");
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
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(episode)
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data?.detail || "Erreur lors de la prédiction");
    }

    return {
      result: Array.isArray(data?.result) ? data.result : []
    };
  } catch (error) {
    return {
      result: []
    };
  }
}