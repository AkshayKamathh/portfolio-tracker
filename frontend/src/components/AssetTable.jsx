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

const colorClass = (value) => {
  if (value > 0) return "positive";
  if (value < 0) return "negative";
  return "";
};

export default function AssetTable({ assets }) {
  if (!assets || assets.length === 0) {
    return (
      <div className="table-wrap">
        <div className="empty-state">No assets yet. Add a transaction to get started.</div>
      </div>
    );
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Quantity</th>
            <th>Avg Buy Price</th>
            <th>Current Price</th>
            <th>Market Value</th>
            <th>Gain / Loss</th>
            <th>Return %</th>
          </tr>
        </thead>
        <tbody>
          {assets.map((a) => (
            <tr key={a.ticker}>
              <td><strong>{a.ticker}</strong></td>
              <td>{fmtQty(a.quantity)}</td>
              <td>{fmtMoney(a.avg_buy_price)}</td>
              <td>{fmtMoney(a.current_price)}</td>
              <td>{fmtMoney(a.market_value)}</td>
              <td className={colorClass(a.gain_loss)}>{fmtMoney(a.gain_loss)}</td>
              <td className={colorClass(a.return_percent)}>
                {(a.return_percent || 0).toFixed(2)}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
