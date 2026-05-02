import { useCallback, useEffect, useState } from "react";
import {
  getTransactionsByTicker,
  getBenchmark,
  getPerformance,
  getPortfolio,
  getTransactions,
  seedDemo,
} from "./api";
import AssetTable from "./components/AssetTable.jsx";
import Charts from "./components/Charts.jsx";
import SummaryCards from "./components/SummaryCards.jsx";
import TransactionForm from "./components/TransactionForm.jsx";
import TransactionTable from "./components/TransactionTable.jsx";
import { downloadTransactionsCsv } from "./utils/exportTransactionsCsv.js";

const EMPTY_PORTFOLIO = {
  total_value: 0,
  total_cost_basis: 0,
  total_gain_loss: 0,
  total_return_percent: 0,
  assets: [],
  warnings: [],
};

export default function App() {
  const [transactions, setTransactions] = useState([]);
  const [portfolio, setPortfolio] = useState(EMPTY_PORTFOLIO);
  const [performance, setPerformance] = useState([]);
  const [benchmark, setBenchmark] = useState([]);
  const [loadingAnalytics, setLoadingAnalytics] = useState(true);
  const [loadingTransactions, setLoadingTransactions] = useState(true);
  const [error, setError] = useState(null);

  const [tickerInput, setTickerInput] = useState("");
  const [tickerFilter, setTickerFilter] = useState("");

  const [seeding, setSeeding] = useState(false);
  const [seedFeedback, setSeedFeedback] = useState(null);
  const [editingTransaction, setEditingTransaction] = useState(null);

  const refreshAnalytics = useCallback(async () => {
    setLoadingAnalytics(true);
    setError(null);
    try {
      const [port, perf, bench] = await Promise.all([
        getPortfolio(),
        getPerformance(),
        getBenchmark(),
      ]);
      setPortfolio(port);
      setPerformance(perf);
      setBenchmark(bench);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingAnalytics(false);
    }
  }, []);

  const refreshTransactions = useCallback(async () => {
    setLoadingTransactions(true);
    setError(null);
    try {
      const txs = tickerFilter
        ? await getTransactionsByTicker(tickerFilter)
        : await getTransactions();
      setTransactions(txs);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingTransactions(false);
    }
  }, [tickerFilter]);

  const refreshAll = useCallback(async () => {
    await refreshAnalytics();
    await refreshTransactions();
  }, [refreshAnalytics, refreshTransactions]);

  useEffect(() => {
    refreshAnalytics();
  }, [refreshAnalytics]);

  useEffect(() => {
    refreshTransactions();
  }, [refreshTransactions]);

  const loading = loadingAnalytics || loadingTransactions;
  const hasAssets = (portfolio?.assets?.length ?? 0) > 0;
  const warnings = portfolio?.warnings || [];

  return (
    <div className="app">
      <header className="header">
        <h1>Portfolio Tracker</h1>
        <p>Track stocks and crypto, see your holdings, and benchmark against the S&amp;P 500.</p>
      </header>

      {error && <div className="app-error">Could not load data: {error}</div>}

      <section className="section">
        <div className="section-title">
          {editingTransaction ? "Edit transaction" : "Add transaction"}
        </div>
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 12 }}>
          <button
            className="btn"
            type="button"
            onClick={async () => {
              setSeeding(true);
              setSeedFeedback(null);
              try {
                await seedDemo();
                setSeedFeedback({ type: "success", message: "Demo data loaded." });
                await refreshAll();
              } catch (err) {
                setSeedFeedback({
                  type: "error",
                  message: err.message || "Failed to seed demo data.",
                });
              } finally {
                setSeeding(false);
              }
            }}
            disabled={seeding}
          >
            {seeding ? "Loading demo..." : "Load demo data"}
          </button>
        </div>
        {seedFeedback && (
          <div className={`feedback ${seedFeedback.type}`}>{seedFeedback.message}</div>
        )}
        <TransactionForm
          editing={editingTransaction}
          onCancelEdit={() => setEditingTransaction(null)}
          onCreated={async () => {
            await refreshAll();
            setEditingTransaction(null);
          }}
        />
      </section>

      <section className="section">
        <div className="section-title">Summary</div>
        {warnings.length > 0 && (
          <div className="warning-banner">
            {warnings.join(" \u2022 ")}
          </div>
        )}
        <SummaryCards portfolio={portfolio} />
      </section>

      <section className="section">
        <div className="section-title">Charts</div>
        {hasAssets ? (
          <Charts
            performance={performance}
            benchmark={benchmark}
            assets={portfolio.assets}
          />
        ) : (
          <div className="card muted empty-state">
            Add your first transaction to unlock charts.
          </div>
        )}
      </section>

      <section className="section">
        <div className="section-title">Holdings</div>
        <AssetTable assets={portfolio.assets} />
      </section>

      <section className="section">
        <div className="section-title">Transactions</div>
        <form
          className="transaction-form"
          onSubmit={(e) => {
            e.preventDefault();
            setTickerFilter((tickerInput || "").trim().toUpperCase());
          }}
          style={{ marginBottom: 12 }}
        >
          <div className="form-field">
            <label htmlFor="tickerFilterInput">Filter by ticker</label>
            <input
              id="tickerFilterInput"
              placeholder="AAPL"
              value={tickerInput}
              onChange={(e) => setTickerInput(e.target.value)}
            />
          </div>
          <div className="form-field">
            <label>&nbsp;</label>
            <button className="btn" type="submit" disabled={loadingTransactions}>
              Apply
            </button>
          </div>
          <div className="form-field">
            <label>&nbsp;</label>
            <button
              className="btn"
              type="button"
              onClick={() => {
                setTickerInput("");
                setTickerFilter("");
              }}
            >
              Clear
            </button>
          </div>
          <div className="form-field">
            <label>&nbsp;</label>
            <button
              className="btn"
              type="button"
              disabled={loadingTransactions || transactions.length === 0}
              onClick={() =>
                downloadTransactionsCsv(
                  transactions,
                  tickerFilter ? `transactions-${tickerFilter}.csv` : undefined,
                )
              }
            >
              Export CSV
            </button>
          </div>
        </form>
        <TransactionTable
          transactions={transactions}
          onDeleted={refreshAll}
          onEdit={(tx) => setEditingTransaction(tx)}
          editingId={editingTransaction?.id ?? null}
          tickerFilter={tickerFilter}
        />
      </section>

      {loading && <div className="loading">Loading...</div>}
    </div>
  );
}
