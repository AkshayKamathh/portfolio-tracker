// Yellow banner at the top that alerts user to when threshold is passed
export default function AlertBanner({ triggered, onDismiss }) {
  if (!triggered || triggered.length === 0) return null;

  return (
    <div
      style={{
        background: "#FAEEDA",
        color: "#633806",
        borderRadius: 8,
        padding: "12px 16px",
        marginBottom: 16,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: triggered.length > 0 ? 8 : 0,
          fontWeight: 500,
          fontSize: 14,
        }}
      >
        <span>
           {triggered.length} price alert{triggered.length === 1 ? "" : "s"} triggered
        </span>
        <button
          type="button"
          onClick={onDismiss}
          style={{
            background: "transparent",
            border: "none",
            color: "#633806",
            fontSize: 13,
            cursor: "pointer",
            textDecoration: "underline",
          }}
        >
          Dismiss all
        </button>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 4, fontSize: 13 }}>
        {triggered.map((a) => (
          <div
            key={a.id}
            style={{ display: "flex", justifyContent: "space-between" }}
          >
            <span>
              <strong>{a.ticker}</strong> {a.direction} ${Number(a.threshold).toFixed(2)}
              {a.note ? ` — ${a.note}` : ""}
            </span>
            <span>fired at ${Number(a.triggered_price ?? 0).toFixed(2)}</span>
          </div>
        ))}
      </div>
    </div>
  );
}