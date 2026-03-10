
const STORAGE_KEY = "meteo-puissante-current-episode";

export function saveEpisode(episode) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(episode));
}

export function loadEpisode() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch (error) {
    console.error("Erreur lecture localStorage:", error);
    return null;
  }
}

export function clearEpisode() {
  localStorage.removeItem(STORAGE_KEY);
}