import { deleteAlert } from "../api";


export default function AlertTable({ alerts, onDeleted }) {
  async function handleDelete(id) {
    try {
      await deleteAlert(id);
      if (onDeleted) await onDeleted();
    } catch (err) {
      alert(`Failed to delete alert: ${err.message}`);
    }
  }

  if (!alerts || alerts.length === 0) {
    return (
      <div className="card muted empty-state">
        No alerts yet. Add one above to get notified when a price crosses your threshold.
      </div>
    );
  }

  return (
    <div className="card" style={{ overflowX: "auto" }}>
      <table className="data-table">
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Direction</th>
            <th>Threshold</th>
            <th>Status</th>
            <th>Note</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {alerts.map((a) => (
            <tr key={a.id}>
              <td><strong>{a.ticker}</strong></td>
              <td>{a.direction}</td>
              <td>${Number(a.threshold).toFixed(2)}</td>
              <td>
                {a.active ? (
                  <span style={{ color: "var(--color-text-success, #1d9e75)" }}>
                    Active
                  </span>
                ) : (
                  <span style={{ color: "var(--color-text-secondary, #888)" }}>
                    Triggered
                  </span>
                )}
              </td>
              <td>{a.note || "—"}</td>
              <td>
                <button
                  className="btn"
                  type="button"
                  onClick={() => handleDelete(a.id)}
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}