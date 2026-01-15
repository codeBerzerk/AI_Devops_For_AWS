from contextlib import asynccontextmanager
from pathlib import Path
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Додати корінь проекту в sys.path, щоб працював запуск `python api/main.py`
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config.settings import settings  # noqa: E402
from utils.logger import logger  # noqa: E402
from api.routes import diagnose, health  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    if settings.EKS_CLUSTER_NAME:
        logger.info(f"EKS Cluster: {settings.EKS_CLUSTER_NAME}")
    else:
        logger.info("Kubernetes: Self-managed cluster (not EKS)")

    # Check Ollama health
    from llm.ollama_client import get_ollama_client

    client = get_ollama_client()

    if not client.health_check():
        logger.warning(
            "⚠️ Ollama не доступний! Перевірте чи запущений: ollama serve",
        )
    else:
        logger.info("✅ Ollama підключений")

    yield

    # Shutdown
    logger.info("👋 Shutting down")


# Create app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(diagnose.router, prefix="/api", tags=["diagnose"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

