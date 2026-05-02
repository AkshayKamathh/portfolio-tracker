"""Application configuration loaded from environment variables."""

import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

MONGO_URI: str | None = os.getenv("MONGO_URI") or None
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "portfolio_tracker")


def _cors_origins() -> list[str]:
    """Build CORS allow-list: comma-separated FRONTEND_ORIGIN, plus localhost/127.0.0.1 for local Vite."""
    raw = (os.getenv("FRONTEND_ORIGIN") or "http://localhost:5173").strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if not parts:
        parts = ["http://localhost:5173"]
    dev_pair = ("http://localhost:5173", "http://127.0.0.1:5173")
    if any(p in dev_pair for p in parts):
        for buddy in dev_pair:
            if buddy not in parts:
                parts.append(buddy)
    return list(dict.fromkeys(parts))


FRONTEND_ORIGINS: list[str] = _cors_origins()
FRONTEND_ORIGIN: str = FRONTEND_ORIGINS[0]
