"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
from starlette.exceptions import HTTPException as StarletteHTTPException

from app import config
from app.routes import portfolio, transactions
from app.routes.demo import router as demo_router

app = FastAPI(title="Portfolio Tracker", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(portfolio.router)
app.include_router(demo_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "http_error",
            "status_code": exc.status_code,
            "detail": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "validation_error",
            "status_code": HTTP_422_UNPROCESSABLE_ENTITY,
            "detail": exc.errors(),
        },
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
