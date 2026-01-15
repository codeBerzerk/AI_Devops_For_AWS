from fastapi import APIRouter

from llm.ollama_client import get_ollama_client
from config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""

    # Check Ollama
    ollama_client = get_ollama_client()
    ollama_status = "healthy" if ollama_client.health_check() else "unhealthy"

    # Check kubectl access (optional)
    kubectl_status = "unknown"
    try:
        from k8s.kubectl_wrapper import kubectl

        result = kubectl.run(["version", "--client"])
        kubectl_status = "healthy" if result["success"] else "unhealthy"
    except Exception:
        pass

    return {
        "status": "healthy",
        "version": settings.VERSION,
        "components": {
            "ollama": ollama_status,
            "kubectl": kubectl_status,
        },
        "config": {
            "model": settings.OLLAMA_MODEL,
            "eks_cluster": settings.EKS_CLUSTER_NAME,
            "language": settings.DEFAULT_LANGUAGE,
        },
    }

