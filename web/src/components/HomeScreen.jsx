function HomeScreen({ hasEpisode, onCreateNew, onResume }) {
  return (
    <section className="card">
      <h2>Accueil</h2>
      <p>
        Choisis de démarrer un nouvel épisode orageux ou de reprendre l’épisode
        actuellement stocké dans le navigateur.
      </p>

      <div className="actions">
        <button onClick={onCreateNew}>Nouvel épisode</button>

        <button onClick={onResume} disabled={!hasEpisode}>
          Reprendre l’épisode en cours
        </button>
      </div>

      {!hasEpisode && (
        <p className="muted">Aucun épisode en cours n’est stocké localement.</p>
      )}
    </section>
  );
}

export default HomeScreen;