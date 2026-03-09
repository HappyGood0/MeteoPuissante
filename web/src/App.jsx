import { useEffect, useState } from "react";
import HomeScreen from "./components/HomeScreen";
import NewEpisodeForm from "./components/NewEpisodeForm";
import CurrentEpisodeView from "./components/CurrentEpisodeView";
import { loadEpisode, saveEpisode, clearEpisode } from "./utils/storage";
import { checkApiHealth, predictEpisode } from "./utils/api";

function App() {
  const [screen, setScreen] = useState("home");
  const [episode, setEpisode] = useState(loadEpisode());
  const [apiStatus, setApiStatus] = useState("loading");

  useEffect(() => {
    async function fetchHealth() {
      const result = await checkApiHealth();
      setApiStatus(result.ok ? "online" : "offline");
    }

    fetchHealth();
  }, []);

  useEffect(() => {
    if (episode) {
      saveEpisode(episode);
      setScreen("current");
    } else {
      setScreen("home");
    }
  }, [episode]);

  async function handleCreateEpisode({ airport, firstEvent }) {
    const newEpisode = {
      id: crypto.randomUUID(),
      airport,
      startedAt: new Date().toISOString(),
      status: "active",
      events: [firstEvent],
      prediction: null
    };

    const prediction = await predictEpisode(newEpisode);

    setEpisode({
      ...newEpisode,
      prediction
    });
  }

  async function handleAddEvent(event) {
    const updatedEpisode = {
      ...episode,
      events: [...episode.events, event]
    };

    const prediction = await predictEpisode(updatedEpisode);

    setEpisode({
      ...updatedEpisode,
      prediction
    });
  }

  function handleStartNew() {
    setScreen("new");
  }

  function handleResume() {
    if (episode) {
      setScreen("current");
    }
  }

  function handleBackHome() {
    setScreen(episode ? "current" : "home");
  }

  function handleResetEpisode() {
    clearEpisode();
    setEpisode(null);
    setScreen("home");
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>Météo Puissante</h1>
          <p>Suivi d’épisodes orageux</p>
        </div>

        <div className={`api-badge api-${apiStatus}`}>
          API: {apiStatus}
        </div>
      </header>

      <main className="app-main">
        {screen === "home" && (
          <HomeScreen
            hasEpisode={Boolean(episode)}
            onCreateNew={handleStartNew}
            onResume={handleResume}
          />
        )}

        {screen === "new" && (
          <NewEpisodeForm
            onCreateEpisode={handleCreateEpisode}
            onCancel={handleBackHome}
          />
        )}

        {screen === "current" && episode && (
          <CurrentEpisodeView
            episode={episode}
            onAddEvent={handleAddEvent}
            onResetEpisode={handleResetEpisode}
            onStartNew={handleStartNew}
          />
        )}
      </main>
    </div>
  );
}

export default App;