function EpisodeHistory({ events }) {
  return (
    <div className="card">
      <h3>Historique des éclairs</h3>

      {events.length === 0 ? (
        <p className="muted">Aucun éclair enregistré pour le moment.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Date</th>
              <th>Distance</th>
              <th>Azimut</th>
              <th>Amplitude</th>
              <th>Maxis</th>
              <th>Type</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event, index) => (
              <tr key={index}>
                <td>{event.date}</td>
                <td>{event.dist}</td>
                <td>{event.azimuth}</td>
                <td>{event.amplitude}</td>
                <td>{event.maxis ?? "-"}</td>
                <td>{event.icloud ? "Nuage" : "Sol"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default EpisodeHistory;