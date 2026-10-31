"""
TrustLens AI - FastAPI Application Entrypoint
Serves REST API endpoints and lightweight, accessible web frontend.
"""

import time
import logging
from collections import defaultdict
from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.core.config import settings
from app.api.routes import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.LOG_LEVEL == "info" else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("trustlens.app")

app = FastAPI(
    title="TrustLens AI",
    description="Explainable document verification and fraud prevention platform powered by Gemma 4.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else ["https://*.cloudwaysapps.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-Memory Rate Limiting
client_request_history = defaultdict(list)


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only rate-limit API calls
    if request.url.path.startswith("/api/analyze"):
        client_ip = request.client.host if request.client else "127.0.0.1"
        now = time.time()
        minute_ago = now - 60.0

        # Filter timestamps within the last 60 seconds
        client_request_history[client_ip] = [
            ts for ts in client_request_history[client_ip] if ts > minute_ago
        ]

        if len(client_request_history[client_ip]) >= settings.RATE_LIMIT_PER_MINUTE:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": f"Rate limit exceeded. Maximum {settings.RATE_LIMIT_PER_MINUTE} requests per minute allowed."
                }
            )

        client_request_history[client_ip].append(now)

    response = await call_next(request)
    return response


# Include API Endpoints
app.include_router(api_router)

# Mount Static Files
STATIC_DIR = Path(__file__).resolve().parent / "static"
if not STATIC_DIR.exists():
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", include_in_schema=False)
async def serve_index():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return JSONResponse(
        content={
            "app": "TrustLens AI",
            "version": "1.0.0",
            "status": "online",
            "docs": "/docs",
            "api_health": "/api/health"
        }
    )


GRAPHIFY_DIR = Path(__file__).resolve().parent.parent / "graphify-out"


@app.get("/graph", include_in_schema=False)
async def serve_graph():
    graph_file = GRAPHIFY_DIR / "graph.html"
    if graph_file.exists():
        return FileResponse(str(graph_file))
    return JSONResponse(status_code=404, content={"error": "Graphify graph.html not found"})


@app.get("/tree", include_in_schema=False)
async def serve_tree():
    tree_file = GRAPHIFY_DIR / "GRAPH_TREE.html"
    if tree_file.exists():
        return FileResponse(str(tree_file))
    return JSONResponse(status_code=404, content={"error": "Graphify GRAPH_TREE.html not found"})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
