"""Aegis API — EU AI Act multi-agent governance orchestrator."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from aegis.db import init_db
from aegis.routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Aegis Governance API",
    description=(
        "Multi-agent EU AI Act conformity assessment drafts for public-sector AI systems. "
        "Demonstration only — not legal advice."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("AEGIS_CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "aegis-api", "version": "0.1.0"}
