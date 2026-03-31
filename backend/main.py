from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from typing import List

from core.config import settings
from core.database import init_db
from api.routes import simulation, agents, reports, god_mode, scenarios
from core.logger import setup_logger

logger = setup_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting RedSwarm API...")
    init_db()
    logger.info("Database initialized")
    yield
    logger.info("Shutting down RedSwarm API...")


app = FastAPI(
    title="RedSwarm API",
    description="AI-Powered Red Team Simulation Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulation.router, prefix="/api/v1/simulation", tags=["Simulation"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(reports.router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(god_mode.router, prefix="/api/v1/god-mode", tags=["God Mode"])
app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["Scenarios"])


@app.get("/")
async def root():
    return {
        "name": "RedSwarm API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "agents": "ready"
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD
    )
