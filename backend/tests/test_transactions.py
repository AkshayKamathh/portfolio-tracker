"""Route-level tests for /transactions using FastAPI's TestClient."""

from bson import ObjectId


def _create_buy(client, ticker="AAPL", quantity=10, price=150, date="2024-01-10", memo=None):
    body = {
        "ticker": ticker,
        "transaction_type": "buy",
        "quantity": quantity,
        "price": price,
        "date": date,
    }
    if memo is not None:
        body["memo"] = memo
    return client.post("/transactions", json=body)


def test_create_buy_transaction(client):
    response = _create_buy(client)
    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["transaction_type"] == "buy"
    assert data["quantity"] == 10
    assert data["price"] == 150
    assert data["date"] == "2024-01-10"
    assert data["memo"] == ""
    assert data["id"]


def test_create_with_memo(client):
    response = _create_buy(client, memo="  trim me  ")
    assert response.status_code == 201
    assert response.json()["memo"] == "trim me"


def test_memo_too_long_rejected(client):
    response = _create_buy(client, memo="x" * 501)
    assert response.status_code == 422


def test_ticker_normalized_to_uppercase(client):
    response = _create_buy(client, ticker="  aapl ")
    assert response.status_code == 201
    assert response.json()["ticker"] == "AAPL"


def test_invalid_quantity_rejected(client):
    response = client.post(
        "/transactions",
        json={
            "ticker": "AAPL",
            "transaction_type": "buy",
            "quantity": 0,
            "price": 100,
            "date": "2024-01-10",
        },
    )
    assert response.status_code == 422


def test_invalid_price_rejected(client):
    response = client.post(
        "/transactions",
        json={
            "ticker": "AAPL",
            "transaction_type": "buy",
            "quantity": 1,
            "price": -5,
            "date": "2024-01-10",
        },
    )
    assert response.status_code == 422


def test_invalid_transaction_type_rejected(client):
    response = client.post(
        "/transactions",
        json={
            "ticker": "AAPL",
            "transaction_type": "trade",
            "quantity": 1,
            "price": 100,
            "date": "2024-01-10",
        },
    )
    assert response.status_code == 422


def test_create_rejects_transaction_date_before_1970(client):
    response = client.post(
        "/transactions",
        json={
            "ticker": "AAPL",
            "transaction_type": "buy",
            "quantity": 1,
            "price": 10,
            "date": "1969-12-31",
        },
    )
    assert response.status_code == 422


def test_create_rejects_transaction_date_after_2100(client):
    response = client.post(
        "/transactions",
        json={
            "ticker": "AAPL",
            "transaction_type": "buy",
            "quantity": 1,
            "price": 10,
            "date": "2101-01-01",
        },
    )
    assert response.status_code == 422


def test_patch_rejects_transaction_date_out_of_range(client):
    created = _create_buy(client, ticker="AAPL", quantity=1, price=10, date="2024-01-10").json()
    response = client.patch(
        f"/transactions/{created['id']}",
        json={"date": "2101-06-01"},
    )
    assert response.status_code == 422


def test_oversell_rejected(client):
    _create_buy(client, ticker="TSLA", quantity=3, price=220, date="2024-04-05")
    response = client.post(
        "/transactions",
        json={
            "ticker": "TSLA",
            "transaction_type": "sell",
            "quantity": 5,
            "price": 230,
            "date": "2024-04-10",
        },
    )
    assert response.status_code == 400
    assert "Cannot sell" in response.json()["detail"]


def test_list_transactions_sorted_newest_first(client):
    _create_buy(client, ticker="AAPL", date="2024-01-10")
    _create_buy(client, ticker="AAPL", date="2024-03-15")
    response = client.get("/transactions")
    assert response.status_code == 200
    dates = [tx["date"] for tx in response.json()]
    assert dates == ["2024-03-15", "2024-01-10"]


def test_list_transactions_filtered_by_ticker(client):
    _create_buy(client, ticker="AAPL", date="2024-01-10")
    _create_buy(client, ticker="MSFT", date="2024-02-20")
    response = client.get("/transactions/aapl")
    assert response.status_code == 200
    tickers = {tx["ticker"] for tx in response.json()}
    assert tickers == {"AAPL"}


def test_delete_transaction(client):
    created = _create_buy(client).json()
    response = client.delete(f"/transactions/{created['id']}")
    assert response.status_code == 200
    assert response.json() == {"message": "Transaction deleted"}

    response = client.get("/transactions")
    assert response.json() == []


def test_delete_invalid_id_returns_404(client):
    response = client.delete("/transactions/not-an-objectid")
    assert response.status_code == 404


def test_delete_unknown_id_returns_404(client):
    response = client.delete(f"/transactions/{ObjectId()}")
    assert response.status_code == 404


def test_patch_transaction_updates_fields(client):
    created = _create_buy(client, ticker="AAPL", quantity=10, price=150, date="2024-01-10").json()
    tx_id = created["id"]
    response = client.patch(
        f"/transactions/{tx_id}",
        json={"quantity": 4, "price": 155, "memo": "rebalance"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 4
    assert data["price"] == 155
    assert data["ticker"] == "AAPL"
    assert data["memo"] == "rebalance"


def test_patch_clears_memo(client):
    created = _create_buy(client, memo="note").json()
    response = client.patch(f"/transactions/{created['id']}", json={"memo": ""})
    assert response.status_code == 200
    assert response.json()["memo"] == ""


def test_patch_empty_body_returns_400(client):
    created = _create_buy(client).json()
    response = client.patch(f"/transactions/{created['id']}", json={})
    assert response.status_code == 400
    assert response.json()["detail"] == "No fields to update"


def test_patch_invalid_id_returns_404(client):
    response = client.patch("/transactions/not-an-objectid", json={"quantity": 1})
    assert response.status_code == 404


def test_patch_unknown_id_returns_404(client):
    response = client.patch(f"/transactions/{ObjectId()}", json={"quantity": 1})
    assert response.status_code == 404


def test_export_transactions_csv_all(client):
    _create_buy(client, ticker="AAPL", quantity=1, price=10, date="2024-01-10")
    _create_buy(client, ticker="MSFT", quantity=2, price=20, date="2024-02-01")
    response = client.get("/transactions/export")
    assert response.status_code == 200
    assert "text/csv" in response.headers.get("content-type", "")
    text = response.content.decode("utf-8-sig")
    lines = text.strip().splitlines()
    assert lines[0] == "id,ticker,transaction_type,quantity,price,date,memo,created_at"
    assert len(lines) == 3


def test_export_transactions_csv_filtered_by_ticker(client):
    _create_buy(client, ticker="AAPL", quantity=1, price=10, date="2024-01-10")
    _create_buy(client, ticker="MSFT", quantity=2, price=20, date="2024-02-01")
    response = client.get("/transactions/export?ticker=MSFT")
    assert response.status_code == 200
    text = response.content.decode("utf-8-sig")
    lines = [ln for ln in text.strip().splitlines() if ln]
    assert len(lines) == 2
    assert "MSFT" in lines[1]
    assert "AAPL" not in lines[1]


def test_patch_oversell_after_edit_rejected(client):
    _create_buy(client, ticker="TSLA", quantity=3, price=220, date="2024-04-05")
    sell = client.post(
        "/transactions",
        json={
            "ticker": "TSLA",
            "transaction_type": "sell",
            "quantity": 2,
            "price": 230,
            "date": "2024-04-10",
        },
    ).json()
    response = client.patch(
        f"/transactions/{sell['id']}",
        json={"quantity": 5},
    )
    assert response.status_code == 400
    assert "Cannot sell" in response.json()["detail"]
