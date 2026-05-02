"""Application configuration loaded from environment variables."""

import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=True))

MONGO_URI: str | None = os.getenv("MONGO_URI") or None
MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "portfolio_tracker")
FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
