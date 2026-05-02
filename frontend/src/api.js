const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (body && body.detail) {
        detail =
          typeof body.detail === "string"
            ? body.detail
            : JSON.stringify(body.detail);
      }
    } catch (_err) {
      // No JSON body; keep default message.
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

export const getTransactions = () => request("/transactions");

export const getTransactionsByTicker = (ticker) =>
  request(`/transactions/${encodeURIComponent(ticker || "")}`);

export const createTransaction = (payload) =>
  request("/transactions", {
    method: "POST",
    body: JSON.stringify(payload),
  });

export const deleteTransaction = (id) =>
  request(`/transactions/${id}`, { method: "DELETE" });

export const updateTransaction = (id, payload) =>
  request(`/transactions/${id}`, {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

export const getPortfolio = () => request("/portfolio");

export const getPerformance = () => request("/performance");

export const getBenchmark = () => request("/benchmark");

export const seedDemo = () => request("/demo/seed", { method: "POST" });
