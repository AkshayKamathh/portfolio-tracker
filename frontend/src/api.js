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
    } catch {
      // response body wasn't JSON
    }
    throw new Error(detail);
  }
  if (response.status === 204) return null;
  return response.json();
}

function withDateRangeQuery(path, { from, to } = {}) {
  const params = new URLSearchParams();
  if (from) params.set("from", from);
  if (to) params.set("to", to);
  const q = params.toString();
  return q ? `${path}?${q}` : path;
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

export const getPerformance = (range = {}) =>
  request(withDateRangeQuery("/performance", range));

export const getBenchmark = (range = {}) =>
  request(withDateRangeQuery("/benchmark", range));

export const seedDemo = () => request("/demo/seed", { method: "POST" });
