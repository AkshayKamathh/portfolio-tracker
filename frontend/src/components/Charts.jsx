import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const PIE_COLORS = [
  "#3b82f6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#8b5cf6",
  "#06b6d4",
  "#ec4899",
  "#84cc16",
];

const fmtCurrency = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value || 0);

function PortfolioValueChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="empty-state">Add a transaction to see portfolio history.</div>;
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
        <YAxis tick={{ fontSize: 11 }} tickFormatter={fmtCurrency} width={70} />
        <Tooltip
          formatter={(value) => fmtCurrency(value)}
          labelStyle={{ color: "#1e293b" }}
        />
        <Line
          type="monotone"
          dataKey="portfolio_value"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          name="Portfolio value"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function BenchmarkChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <div className="empty-state">
        Benchmark data will appear once price history is available.
      </div>
    );
  }
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
        <CartesianGrid stroke="#e2e8f0" strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} minTickGap={24} />
        <YAxis
          tick={{ fontSize: 11 }}
          tickFormatter={(v) => `${v.toFixed(0)}%`}
          width={50}
        />
        <Tooltip
          formatter={(value) => `${Number(value).toFixed(2)}%`}
          labelStyle={{ color: "#1e293b" }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="portfolio_return"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          name="Portfolio"
        />
        <Line
          type="monotone"
          dataKey="benchmark_return"
          stroke="#f59e0b"
          strokeWidth={2}
          dot={false}
          name="S&P 500 (SPY)"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

function AllocationChart({ assets }) {
  const data = (assets || [])
    .filter((a) => a.market_value > 0)
    .map((a) => ({ name: a.ticker, value: a.market_value }));

  if (data.length === 0) {
    return <div className="empty-state">No holdings yet.</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Tooltip
          formatter={(value) => fmtCurrency(value)}
          labelStyle={{ color: "#1e293b" }}
        />
        <Legend />
        <Pie
          data={data}
          dataKey="value"
          nameKey="name"
          cx="50%"
          cy="50%"
          outerRadius={90}
          label={({ name, percent }) =>
            `${name} ${(percent * 100).toFixed(0)}%`
          }
        >
          {data.map((_, idx) => (
            <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
          ))}
        </Pie>
      </PieChart>
    </ResponsiveContainer>
  );
}

export default function Charts({ performance, benchmark, assets }) {
  return (
    <div className="chart-grid">
      <div className="chart-card full">
        <h3>Portfolio value over time</h3>
        <PortfolioValueChart data={performance} />
      </div>
      <div className="chart-card">
        <h3>Portfolio vs S&amp;P 500</h3>
        <BenchmarkChart data={benchmark} />
      </div>
      <div className="chart-card">
        <h3>Asset allocation</h3>
        <AllocationChart assets={assets} />
      </div>
    </div>
  );
}
