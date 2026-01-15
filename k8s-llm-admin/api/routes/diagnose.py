from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

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
async def diagnose_stream(request: DiagnoseRequest):
    """
    Streaming діагностика (Server-Sent Events)
    
    Відповідь приходить потоково, частинами, як тільки LLM генерує текст.
    
    **Приклад використання з curl:**
    ```bash
    curl -N -X POST http://localhost:8000/api/diagnose/stream \
      -H "Content-Type: application/json" \
      -d '{
        "message": "Мій pod в CrashLoopBackOff, що робити?",
        "resource_type": "pod",
        "language": "uk"
      }'
    ```
    
    **Приклад з Python:**
    ```python
    import requests
    response = requests.post(
        "http://localhost:8000/api/diagnose/stream",
        json={"message": "Тест", "language": "uk"},
        stream=True
    )
    for line in response.iter_lines():
        if line:
            data = json.loads(line)
            print(data.get("chunk", ""), end="", flush=True)
    ```
    """
    try:
        logger.info(
            f"Отримано streaming запит на діагностику: {request.message[:50]}...",
        )
        
        # Конвертувати language string → enum
        lang = Language.UKRAINIAN if request.language == "uk" else Language.ENGLISH
        
        # Створити diagnostic request
        diag_req = DiagnosticRequest(
            user_message=request.message,
            resource_type=request.resource_type,
            namespace=request.namespace,
            kubectl_output=request.kubectl_output,
            language=lang,
            cluster_context=None,
        )
        
        def generate_stream():
            """Generator для SSE streaming"""
            try:
                for chunk in orchestrator.diagnose_stream(diag_req):
                    # Формат SSE: data: {json}\n\n
                    data = json.dumps({"chunk": chunk, "done": False})
                    yield f"data: {data}\n\n"
                
                # Фінальне повідомлення
                final = json.dumps({"chunk": "", "done": True})
                yield f"data: {final}\n\n"
            
            except Exception as e:
                logger.error(f"Помилка streaming: {e}")
                error_data = json.dumps({"error": str(e), "done": True})
                yield f"data: {error_data}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Вимкнути буферизацію в nginx
            }
        )
    
    except Exception as e:
        logger.error(f"Помилка streaming діагностики: {e}")
        raise HTTPException(status_code=500, detail=str(e))

