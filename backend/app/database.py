"""MongoDB connection helpers (lazy client; tests patch out the collection)."""

from __future__ import annotations

import os

import certifi
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from app import config

_client: MongoClient | None = None


def _get_client() -> MongoClient:
    global _client
    if _client is None:
        if not config.MONGO_URI:
            raise RuntimeError(
                "MONGO_URI is not set. Add it to your .env before running the backend."
            )
        # certifi bundle avoids TLS verify failures on some macOS Python installs.
        kwargs: dict = {"tlsCAFile": certifi.where()}
        ssl_cert_file = os.getenv("SSL_CERT_FILE")
        if ssl_cert_file:
            kwargs["tlsCAFile"] = ssl_cert_file

        _client = MongoClient(config.MONGO_URI, **kwargs)
    return _client


def get_db() -> Database:
    return _get_client()[config.MONGO_DB_NAME]


def get_transactions_collection() -> Collection:
    return get_db()["transactions"]
