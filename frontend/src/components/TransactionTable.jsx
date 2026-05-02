import { useState } from "react";
import { deleteTransaction } from "../api";

const fmtMoney = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value || 0);

const fmtQty = (value) => {
  const n = Number(value || 0);
  return Number.isInteger(n) ? n.toString() : n.toFixed(4);
};

export default function TransactionTable({
  transactions,
  onDeleted,
  onEdit,
  editingId,
  tickerFilter,
}) {
  const [deletingId, setDeletingId] = useState(null);
  const [error, setError] = useState(null);

  if (!transactions || transactions.length === 0) {
    return (
      <div className="table-wrap">
        <div className="empty-state">
          {tickerFilter ? `No transactions for ${tickerFilter}.` : "No transactions yet."}
        </div>
      </div>
    );
  }

  const handleDelete = async (id) => {
    setDeletingId(id);
    setError(null);
    try {
      await deleteTransaction(id);
      if (onDeleted) onDeleted();
    } catch (err) {
      setError(err.message);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="table-wrap">
      {error && <div className="warning-banner">{error}</div>}
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Type</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Date</th>
            <th>Memo</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td><strong>{tx.ticker}</strong></td>
              <td style={{ textTransform: "capitalize" }}>{tx.transaction_type}</td>
              <td>{fmtQty(tx.quantity)}</td>
              <td>{fmtMoney(tx.price)}</td>
              <td>{tx.date}</td>
              <td
                className="memo-cell"
                title={tx.memo || undefined}
              >
                {tx.memo || "—"}
              </td>
              <td>
                <div style={{ display: "flex", gap: 8, flexWrap: "wrap", justifyContent: "flex-end" }}>
                  {onEdit && (
                    <button
                      className="btn"
                      type="button"
                      onClick={() => onEdit(tx)}
                      disabled={editingId === tx.id}
                    >
                      {editingId === tx.id ? "Editing..." : "Edit"}
                    </button>
                  )}
                  <button
                    className="btn-danger"
                    type="button"
                    onClick={() => handleDelete(tx.id)}
                    disabled={deletingId === tx.id || editingId === tx.id}
                  >
                    {deletingId === tx.id ? "Deleting..." : "Delete"}
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
