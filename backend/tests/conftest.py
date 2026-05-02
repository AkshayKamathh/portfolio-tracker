"""Pytest fixtures; route tests use an in-memory collection (no Atlas)."""

from datetime import datetime
from typing import Any

import pytest
from bson import ObjectId
from fastapi.testclient import TestClient


class FakeCollection:
    """Tiny stand-in for PyMongo in route tests."""

    def __init__(self) -> None:
        self.docs: list[dict] = []

    def insert_one(self, doc: dict):
        doc = dict(doc)
        doc["_id"] = ObjectId()
        self.docs.append(doc)
        return type("InsertResult", (), {"inserted_id": doc["_id"]})()

    def find(self, query: dict | None = None):
        query = query or {}
        matches = [d for d in self.docs if self._matches(d, query)]
        return _FakeSortedDocs(matches)

    def delete_one(self, query: dict):
        for i, d in enumerate(self.docs):
            if self._matches(d, query):
                del self.docs[i]
                return type("DeleteResult", (), {"deleted_count": 1})()
        return type("DeleteResult", (), {"deleted_count": 0})()

    def delete_many(self, query: dict):
        to_delete = [i for i, d in enumerate(self.docs) if self._matches(d, query)]
        for i in reversed(to_delete):
            del self.docs[i]
        return type("DeleteResult", (), {"deleted_count": len(to_delete)})()

    def find_one(self, query: dict):
        for d in self.docs:
            if self._matches(d, query):
                return dict(d)
        return None

    def update_one(self, query: dict, update: dict):
        sets = update.get("$set") or {}
        for i, d in enumerate(self.docs):
            if self._matches(d, query):
                for key, value in sets.items():
                    self.docs[i][key] = value
                return type("UpdateResult", (), {"modified_count": 1})()
        return type("UpdateResult", (), {"modified_count": 0})()

    @staticmethod
    def _matches(doc: dict, query: dict) -> bool:
        for key, value in query.items():
            if isinstance(value, dict) and "$in" in value:
                if doc.get(key) not in value["$in"]:
                    return False
                continue
            if doc.get(key) != value:
                return False
        return True


class _FakeSortedDocs:
    def __init__(self, docs: list[dict]):
        self.docs = list(docs)

    def sort(self, spec: list[tuple[str, int]]):
        def key(doc: dict):
            parts = []
            for field, _ in spec:
                v = doc.get(field)
                if isinstance(v, datetime):
                    parts.append(v.timestamp())
                elif v is None:
                    parts.append("")
                else:
                    parts.append(v)
            return tuple(parts)

        for field, direction in reversed(spec):
            self.docs.sort(
                key=lambda d, f=field: (d.get(f) is None, d.get(f) or ""),
                reverse=(direction == -1),
            )
        return self

    def __iter__(self):
        return iter(self.docs)


@pytest.fixture
def fake_collection():
    return FakeCollection()


@pytest.fixture
def client(fake_collection, monkeypatch):
    from app import main
    from app.routes import portfolio as portfolio_routes
    from app.routes import transactions as transactions_routes
    from app.routes import demo as demo_routes

    monkeypatch.setattr(
        transactions_routes, "get_transactions_collection", lambda: fake_collection
    )
    monkeypatch.setattr(
        portfolio_routes, "get_transactions_collection", lambda: fake_collection
    )
    monkeypatch.setattr(
        demo_routes, "get_transactions_collection", lambda: fake_collection
    )

    return TestClient(main.app)
