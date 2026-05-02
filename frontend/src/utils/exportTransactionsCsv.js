function escapeCsvCell(value) {
  const s = String(value ?? "");
  if (/[",\n\r]/.test(s)) {
    return `"${s.replace(/"/g, '""')}"`;
  }
  return s;
}

/** Download the given transaction rows as a UTF-8 CSV (BOM prefix for Excel). */
export function downloadTransactionsCsv(transactions, filename) {
  const headers = [
    "id",
    "ticker",
    "transaction_type",
    "quantity",
    "price",
    "date",
    "created_at",
  ];
  const lines = [
    headers.join(","),
    ...transactions.map((tx) =>
      headers.map((key) => escapeCsvCell(tx[key])).join(","),
    ),
  ];
  const body = lines.join("\r\n");
  const defaultName = `transactions-${new Date().toISOString().slice(0, 10)}.csv`;
  const blob = new Blob(["\uFEFF", body], {
    type: "text/csv;charset=utf-8;",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename || defaultName;
  anchor.click();
  URL.revokeObjectURL(url);
}
