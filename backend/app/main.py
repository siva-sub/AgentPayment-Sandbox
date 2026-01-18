"""AgentPayment Sandbox API - Main Application."""

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import flows, protocols, runs, scenarios, inspector, security
from app.mock import ucp_router, acp_router, x402_router, ap2_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("🚀 AgentPayment Sandbox starting...")
    yield
    # Shutdown
    print("👋 AgentPayment Sandbox shutting down...")


app = FastAPI(
    title="AgentPayment Sandbox",
    description="Postman + Chaos Monkey + Case Manager for Agent Payments",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://siva-sub.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(protocols.router, prefix="/api/protocols", tags=["Protocols"])
app.include_router(scenarios.router, prefix="/api/scenarios", tags=["Scenarios"])
app.include_router(runs.router, prefix="/api/runs", tags=["Runs"])
app.include_router(flows.router, prefix="/api/flows", tags=["Flows"])
app.include_router(inspector.router, prefix="/api/inspector", tags=["Inspector"])
app.include_router(security.router, prefix="/api/security", tags=["Security"])

# Mock server endpoints
app.include_router(ucp_router, prefix="/mock/ucp", tags=["Mock UCP"])
app.include_router(acp_router, prefix="/mock/acp", tags=["Mock ACP"])
app.include_router(x402_router, prefix="/mock/x402", tags=["Mock x402"])
app.include_router(ap2_router, prefix="/mock/ap2", tags=["Mock AP2"])


@app.get("/")
async def root() -> dict[str, Any]:
    """Root endpoint."""
    return {
        "name": "AgentPayment Sandbox",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
