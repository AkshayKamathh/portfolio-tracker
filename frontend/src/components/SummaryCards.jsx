const fmtMoney = (value) =>
  new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 2,
  }).format(value || 0);

const fmtPercent = (value) => `${(value || 0).toFixed(2)}%`;

const colorClass = (value) => {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "";
};

export default function SummaryCards({ portfolio }) {
  const data = portfolio || {
    total_value: 0,
    total_cost_basis: 0,
    total_gain_loss: 0,
    total_return_percent: 0,
  };

  const cards = [
    { label: "Total Value", value: fmtMoney(data.total_value), tone: "" },
    { label: "Cost Basis", value: fmtMoney(data.total_cost_basis), tone: "" },
    {
      label: "Gain / Loss",
      value: fmtMoney(data.total_gain_loss),
      tone: colorClass(data.total_gain_loss),
    },
    {
      label: "Return %",
      value: fmtPercent(data.total_return_percent),
      tone: colorClass(data.total_return_percent),
    },
  ];

  return (
    <div className="summary-grid">
      {cards.map((c) => (
        <div key={c.label} className="card summary-card">
          <div className="label">{c.label}</div>
          <div className={`value ${c.tone}`}>{c.value}</div>
        </div>
      ))}
    </div>
  );
}
