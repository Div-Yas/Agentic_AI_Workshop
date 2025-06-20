from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import json
from typing import Dict, Any

from .config import settings
from .api.routes import router as api_router
from .api.websocket import websocket_endpoint

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Agentic AI-Based Autonomous Payroll & Tax Planner",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Add WebSocket endpoint
app.add_websocket_route("/ws", websocket_endpoint)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Agentic AI-Based Autonomous Payroll & Tax Planner",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "agents": "/api/v1/agents"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Internal server error",
            "detail": str(exc)
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    ) 