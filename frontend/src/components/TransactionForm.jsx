import { useEffect, useState } from "react";
import { createTransaction, updateTransaction } from "../api";

const today = () => new Date().toISOString().slice(0, 10);

const emptyForm = () => ({
  ticker: "",
  transaction_type: "buy",
  quantity: "",
  price: "",
  date: today(),
});

export default function TransactionForm({ editing, onCancelEdit, onCreated }) {
  const [form, setForm] = useState(emptyForm);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);

  useEffect(() => {
    if (editing) {
      setFeedback(null);
      setForm({
        ticker: editing.ticker,
        transaction_type: editing.transaction_type,
        quantity: String(editing.quantity),
        price: String(editing.price),
        date: (editing.date || "").slice(0, 10),
      });
    } else {
      setForm(emptyForm());
    }
  }, [editing]);

  const update = (field) => (event) => {
    setForm((prev) => ({ ...prev, [field]: event.target.value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setFeedback(null);
    try {
      const payload = {
        ticker: form.ticker.trim().toUpperCase(),
        transaction_type: form.transaction_type,
        quantity: Number(form.quantity),
        price: Number(form.price),
        date: form.date,
      };
      if (editing) {
        await updateTransaction(editing.id, payload);
        setFeedback({ type: "success", message: "Transaction updated." });
      } else {
        await createTransaction(payload);
        setFeedback({ type: "success", message: "Transaction added." });
        setForm(emptyForm());
      }
      if (onCreated) await onCreated();
    } catch (err) {
      setFeedback({ type: "error", message: err.message });
    } finally {
      setSubmitting(false);
    }
  };

  const isEditing = Boolean(editing);

  return (
    <form className="card" onSubmit={handleSubmit}>
      <div className="transaction-form">
        <div className="form-field">
          <label htmlFor="ticker">Ticker</label>
          <input
            id="ticker"
            placeholder="AAPL"
            value={form.ticker}
            onChange={update("ticker")}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="type">Type</label>
          <select
            id="type"
            value={form.transaction_type}
            onChange={update("transaction_type")}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </div>
        <div className="form-field">
          <label htmlFor="quantity">Quantity</label>
          <input
            id="quantity"
            type="number"
            min="0"
            step="any"
            placeholder="10"
            value={form.quantity}
            onChange={update("quantity")}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="price">Price</label>
          <input
            id="price"
            type="number"
            min="0"
            step="any"
            placeholder="180.25"
            value={form.price}
            onChange={update("price")}
            required
          />
        </div>
        <div className="form-field">
          <label htmlFor="date">Date</label>
          <input
            id="date"
            type="date"
            value={form.date}
            onChange={update("date")}
            required
          />
        </div>
        <div className="form-field">
          <label>&nbsp;</label>
          <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
            {isEditing && (
              <button
                className="btn"
                type="button"
                disabled={submitting}
                onClick={() => {
                  setFeedback(null);
                  if (onCancelEdit) onCancelEdit();
                }}
              >
                Cancel
              </button>
            )}
            <button className="btn" type="submit" disabled={submitting}>
              {submitting
                ? isEditing
                  ? "Saving..."
                  : "Adding..."
                : isEditing
                  ? "Save changes"
                  : "Add transaction"}
            </button>
          </div>
        </div>
      </div>
      {feedback && (
        <div className={`feedback ${feedback.type}`}>{feedback.message}</div>
      )}
    </form>
  );
}
