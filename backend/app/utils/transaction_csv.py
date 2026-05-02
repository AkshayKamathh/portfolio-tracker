"""CSV bytes for transaction exports (same column order as the UI table)."""

import csv
import io

HEADERS = [
    "id",
    "ticker",
    "transaction_type",
    "quantity",
    "price",
    "date",
    "memo",
    "created_at",
]


def transactions_csv_bytes(rows: list[dict], *, ticker_filter: str | None) -> tuple[bytes, str]:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(HEADERS)
    for row in rows:
        writer.writerow([row.get(h, "") for h in HEADERS])
    text = "\ufeff" + buf.getvalue()
    name = f"transactions-{ticker_filter}.csv" if ticker_filter else "transactions.csv"
    return text.encode("utf-8"), name
