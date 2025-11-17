"""FastAPI application entry point."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import database
from app.models import company, forecast, risk_report, simulation, transaction, user  # noqa: F401
from app.routers import anomalies, auth, forecast as forecast_router, ingest, risk, simulate

app = FastAPI(title="AI Financial Risk Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(risk.router)
app.include_router(forecast_router.router)
app.include_router(simulate.router)
app.include_router(anomalies.router)


@app.get("/")
def root() -> dict:
    return {"message": "AI Financial Risk Engine", "docs_url": "/docs"}


@app.on_event("startup")
def on_startup() -> None:
    database.Base.metadata.create_all(bind=database.engine)
