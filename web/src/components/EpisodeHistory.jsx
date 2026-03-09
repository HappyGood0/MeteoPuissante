
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
              <th>Lat</th>
              <th>Lon</th>
              <th>Amplitude</th>
              <th>Maxis</th>
              <th>Icloud</th>
            </tr>
          </thead>
          <tbody>
            {events.map((event, index) => (
              <tr key={index}>
                <td>{event.date}</td>
                <td>{event.lat}</td>
                <td>{event.lon}</td>
                <td>{event.amplitude}</td>
                <td>{event.maxis ?? "-"}</td>
                <td>{String(event.icloud)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default EpisodeHistory;