from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from llm.prompt_manager import orchestrator, DiagnosticRequest
from prompts.multilang_prompts import Language
from utils.logger import logger

router = APIRouter()


class DiagnoseRequest(BaseModel):
    """Request schema для діагностики"""

    message: str
    resource_type: Optional[str] = None
    namespace: str = "default"
    kubectl_output: Optional[str] = None
    language: Optional[str] = "uk"


class DiagnoseResponse(BaseModel):
    """Response schema"""

    diagnosis: str
    model: str
    generation_time: float
    tokens_generated: int


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose_issue(request: DiagnoseRequest):
    """
    Діагностика Kubernetes проблеми

    **Приклад запиту:**
    ```json
    {
      "message": "Мій под в CrashLoopBackOff, що робити?",
      "resource_type": "pod",
      "namespace": "production"
    }
    ```
    """
    try:
        logger.info(
            f"Отримано запит на діагностику: {request.message[:50]}...",
        )

        # Конвертувати language string → enum
        lang = Language.UKRAINIAN if request.language == "uk" else Language.ENGLISH

        # Створити diagnostic request (cluster_context опціональний)
        diag_req = DiagnosticRequest(
            user_message=request.message,
            resource_type=request.resource_type,
            namespace=request.namespace,
            kubectl_output=request.kubectl_output,
            language=lang,
            cluster_context=None,  # Можна додати з settings або залишити None
        )

        # Виконати діагностику
        response = orchestrator.diagnose(diag_req)

        return DiagnoseResponse(
            diagnosis=response.text,
            model=response.model,
            generation_time=response.generation_time,
            tokens_generated=response.tokens_generated,
        )

    except Exception as e:
        logger.error(f"Помилка діагностики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnose/stream")
async def diagnose_stream(request: DiagnoseRequest):  # pragma: no cover - ще не реалізовано
    """Streaming діагностика (SSE)"""
    # TODO: Implement streaming
    raise HTTPException(status_code=501, detail="Streaming not implemented yet")

