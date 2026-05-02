"""Route-level tests for /transactions using FastAPI's TestClient."""

from bson import ObjectId


def _create_buy(client, ticker="AAPL", quantity=10, price=150, date="2024-01-10"):
    return client.post(
        "/transactions",
        json={
            "ticker": ticker,
            "transaction_type": "buy",
            "quantity": quantity,
            "price": price,
            "date": date,
        },
    )


def test_create_buy_transaction(client):
    response = _create_buy(client)
    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["transaction_type"] == "buy"
    assert data["quantity"] == 10
    assert data["price"] == 150
    assert data["date"] == "2024-01-10"
    assert data["id"]


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
        json={"quantity": 4, "price": 155},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["quantity"] == 4
    assert data["price"] == 155
    assert data["ticker"] == "AAPL"


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
