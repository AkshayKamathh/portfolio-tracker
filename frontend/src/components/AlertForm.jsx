import { useState } from "react";
import { createAlert } from "../api";

// Form for creating a new price alert.

export default function AlertForm({ onCreated }) {
  const [ticker, setTicker] = useState("");
  const [direction, setDirection] = useState("below");
  const [threshold, setThreshold] = useState("");
  const [note, setNote] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setSubmitting(true);
    setFeedback(null);
    try {
      const payload = {
        ticker: ticker.trim().toUpperCase(),
        direction,
        threshold: parseFloat(threshold),
      };
      // Only include note if user actually wrote one — matches transaction memo handling
      const trimmedNote = note.trim();
      if (trimmedNote) payload.note = trimmedNote;

      await createAlert(payload);

      // Reset the form so the user can add another quickly
      setTicker("");
      setThreshold("");
      setNote("");
      setFeedback({ type: "success", message: "Alert created." });
      // Tell parent to refetch the alerts list
      if (onCreated) await onCreated();
    } catch (err) {
      setFeedback({ type: "error", message: err.message || "Failed to create alert." });
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <>
      {feedback && (
        <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
      )}
      <form className="transaction-form" onSubmit={handleSubmit}>
        <div className="form-field">
          <label htmlFor="alertTicker">Ticker</label>
          <input
            id="alertTicker"
            placeholder="AAPL"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="alertDirection">When price is</label>
          <select
            id="alertDirection"
            value={direction}
            onChange={(e) => setDirection(e.target.value)}
          >
            <option value="below">below</option>
            <option value="above">above</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="alertThreshold">Threshold ($)</label>
          <input
            id="alertThreshold"
            type="number"
            step="0.01"
            min="0.01"
            placeholder="150.00"
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
            required
          />
        </div>
        <div className="form-field" style={{ gridColumn: "1 / -1" }}>
          <label htmlFor="alertNote">Note (optional)</label>
          <input
            id="alertNote"
            placeholder="e.g. stop loss, swing entry"
            value={note}
            onChange={(e) => setNote(e.target.value)}
            maxLength={500}
          />
        </div>
        <div className="form-field">
          <label>&nbsp;</label>
          <button className="btn" type="submit" disabled={submitting}>
            {submitting ? "Adding..." : "Add alert"}
          </button>
        </div>
      </form>
    </>
  );
}