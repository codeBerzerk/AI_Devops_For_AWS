# 📝 Детальна інструкція імплементації K8s LLM Admin

## 🎯 Поточний статус проекту

**Структура створена ✅**  
**Що треба зробити:** Заповнити файли функціональністю

---

## 📁 Файли що вже ГОТОВІ (не треба міняти)

✅ **k8s_prompt_engineering.py** - Базові промпти (англійською)  
✅ **multilang_prompts.py** - Українська система промптів  
✅ **eks_integration.py** - AWS EKS wrapper  

---

## 🔧 Файли що ТРЕБА ДОПИСАТИ

### 1️⃣ **`config/settings.py`** - Налаштування

**Що є зараз:** Порожній файл  
**Що додати:** Конфігурація через Pydantic

```python
# config/settings.py

from pydantic import BaseSettings, Field
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Налаштування проекту"""
    
    # Project
    PROJECT_NAME: str = "K8s LLM Admin"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # Ollama LLM
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", env="OLLAMA_URL")
    OLLAMA_MODEL: str = Field(default="llama3.2:3b-instruct", env="OLLAMA_MODEL")
    OLLAMA_TIMEOUT: int = Field(default=120, env="OLLAMA_TIMEOUT")
    
    # LLM Parameters
    LLM_TEMPERATURE: float = Field(default=0.7, env="LLM_TEMPERATURE")
    LLM_MAX_TOKENS: int = Field(default=2000, env="LLM_MAX_TOKENS")
    
    # AWS EKS
    AWS_REGION: str = Field(default="eu-west-1", env="AWS_REGION")
    AWS_PROFILE: Optional[str] = Field(default=None, env="AWS_PROFILE")
    EKS_CLUSTER_NAME: str = Field(default="", env="EKS_CLUSTER_NAME")
    
    # Kubernetes
    KUBECONFIG_PATH: Optional[str] = Field(default=None, env="KUBECONFIG")
    DEFAULT_NAMESPACE: str = Field(default="default", env="K8S_NAMESPACE")
    
    # Language
    DEFAULT_LANGUAGE: str = Field(default="uk", env="DEFAULT_LANGUAGE")
    
    # API
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    CORS_ORIGINS: list = Field(default=["*"], env="CORS_ORIGINS")
    
    # Security
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    RATE_LIMIT: int = Field(default=30, env="RATE_LIMIT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_DIR: Path = Field(default=Path("./logs"), env="LOG_DIR")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Створити директорії
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
```

**Пріоритет:** 🔥 ВИСОКИЙ (потрібен для всього іншого)

---

### 2️⃣ **`utils/logger.py`** - Логування

**Що є:** Порожній `__init__.py`  
**Що додати:** Налаштування loguru

```python
# utils/logger.py

import sys
from loguru import logger
from config.settings import settings

# Видалити default handler
logger.remove()

# Console handler (з кольорами)
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True
)

# File handler (всі логи)
if settings.LOG_DIR:
    logger.add(
        settings.LOG_DIR / "app.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # Error logs окремо
    logger.add(
        settings.LOG_DIR / "errors.log",
        level="ERROR",
        rotation="5 MB",
        retention="14 days",
        compression="zip"
    )

# Export
__all__ = ["logger"]
```

**Пріоритет:** 🔥 ВИСОКИЙ

---

### 3️⃣ **`llm/ollama_client.py`** - LLM Client

**Статус:** Вже створений в artifacts  
**Що зробити:** Скопіювати з artifact "K8s LLM Admin - Повний План Проекту", розділ "llm/ollama_client.py"

**Додати також:**

```python
# llm/ollama_client.py (в кінець файлу)

# Singleton instance
_ollama_client = None

def get_ollama_client() -> OllamaClient:
    """Get global Ollama client instance"""
    global _ollama_client
    
    if _ollama_client is None:
        from config.settings import settings
        _ollama_client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.OLLAMA_TIMEOUT
        )
    
    return _ollama_client
```

**Пріоритет:** 🔥 КРИТИЧНИЙ

---

### 4️⃣ **`llm/prompt_manager.py`** - Orchestration промптів

**Що є:** Порожній файл  
**Що додати:** Інтеграція всіх систем промптів

```python
# llm/prompt_manager.py

from typing import Dict, Optional, Any
from dataclasses import dataclass

from prompts.multilang_prompts import (
    prompt_manager,
    Language,
    detect_language
)
from llm.ollama_client import get_ollama_client, LLMResponse
from utils.logger import logger


@dataclass
class DiagnosticRequest:
    """Запит на діагностику"""
    user_message: str
    resource_type: Optional[str] = None
    namespace: str = "default"
    kubectl_output: Optional[str] = None
    language: Optional[Language] = None
    eks_context: Optional[Dict] = None


class PromptOrchestrator:
    """Оркестрація промптів та LLM"""
    
    def __init__(self):
        self.llm_client = get_ollama_client()
        self.prompt_manager = prompt_manager
    
    def diagnose(self, request: DiagnosticRequest) -> LLMResponse:
        """
        Головна функція діагностики
        
        Args:
            request: Diagnostic request
        
        Returns:
            LLM response з діагнозом
        """
        # 1. Визначити мову якщо не вказана
        language = request.language
        if not language:
            detected = detect_language(request.user_message)
            language = detected
            logger.info(f"Визначена мова: {detected.value}")
        
        # 2. Згенерувати промпт
        full_prompt = self.prompt_manager.build_full_prompt(
            user_message=request.user_message,
            resource_type=request.resource_type,
            language=language,
            eks_context=request.eks_context
        )
        
        logger.debug(f"Згенерований промпт (довжина: {len(full_prompt)} chars)")
        
        # 3. Відправити до LLM
        try:
            response = self.llm_client.generate(
                prompt=full_prompt,
                temperature=0.7,
                max_tokens=2000
            )
            
            logger.info(
                f"LLM відповів за {response.generation_time:.2f}s, "
                f"згенеровано {response.tokens_generated} токенів"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Помилка LLM генерації: {e}")
            raise
    
    def chat(
        self,
        messages: list,
        language: Language = Language.UKRAINIAN
    ) -> LLMResponse:
        """Multi-turn conversation"""
        
        # Додати system prompt
        system_prompt = self.prompt_manager.get_system_prompt(
            language=language,
            include_cloud=True
        )
        
        messages_with_system = [
            {"role": "system", "content": system_prompt}
        ] + messages
        
        return self.llm_client.chat(messages_with_system)


# Global instance
orchestrator = PromptOrchestrator()
```

**Пріоритет:** 🔥 КРИТИЧНИЙ

---

### 5️⃣ **`k8s/kubectl_wrapper.py`** - Generic kubectl wrapper

**Що додати:**

```python
# k8s/kubectl_wrapper.py

import subprocess
import json
from typing import Dict, List, Optional, Any
from utils.logger import logger


class KubectlWrapper:
    """Generic kubectl wrapper (не EKS-специфічний)"""
    
    def __init__(self, kubeconfig: Optional[str] = None):
        self.kubeconfig = kubeconfig
    
    def _build_command(self, command: List[str]) -> List[str]:
        """Build kubectl command with kubeconfig"""
        cmd = ["kubectl"]
        
        if self.kubeconfig:
            cmd.extend(["--kubeconfig", self.kubeconfig])
        
        cmd.extend(command)
        return cmd
    
    def run(
        self,
        command: List[str],
        namespace: Optional[str] = None,
        output_format: str = "json"
    ) -> Dict[str, Any]:
        """
        Execute kubectl command
        
        Args:
            command: kubectl args (without 'kubectl')
            namespace: k8s namespace
            output_format: json, yaml, or wide
        
        Returns:
            Result dict
        """
        full_cmd = self._build_command(command)
        
        if namespace:
            full_cmd.extend(["-n", namespace])
        
        if output_format and output_format in ["json", "yaml"]:
            full_cmd.extend(["-o", output_format])
        
        try:
            logger.debug(f"Виконання: {' '.join(full_cmd)}")
            
            result = subprocess.run(
                full_cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "command": ' '.join(full_cmd)
            }
        
        except subprocess.TimeoutExpired:
            logger.error(f"Kubectl timeout: {' '.join(full_cmd)}")
            return {
                "success": False,
                "error": "Command timeout",
                "command": ' '.join(full_cmd)
            }
        
        except Exception as e:
            logger.error(f"Kubectl error: {e}")
            return {
                "success": False,
                "error": str(e),
                "command": ' '.join(full_cmd)
            }
    
    def get(
        self,
        resource: str,
        name: Optional[str] = None,
        namespace: Optional[str] = None,
        label_selector: Optional[str] = None
    ) -> Dict:
        """kubectl get"""
        cmd = ["get", resource]
        
        if name:
            cmd.append(name)
        
        if label_selector:
            cmd.extend(["-l", label_selector])
        
        result = self.run(cmd, namespace=namespace, output_format="json")
        
        if result["success"]:
            try:
                return json.loads(result["stdout"])
            except:
                return {}
        
        return {}
    
    def describe(
        self,
        resource: str,
        name: str,
        namespace: Optional[str] = None
    ) -> str:
        """kubectl describe"""
        cmd = ["describe", resource, name]
        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")
    
    def logs(
        self,
        pod_name: str,
        namespace: Optional[str] = None,
        container: Optional[str] = None,
        previous: bool = False,
        tail: int = 100
    ) -> str:
        """kubectl logs"""
        cmd = ["logs", pod_name, f"--tail={tail}"]
        
        if container:
            cmd.extend(["-c", container])
        
        if previous:
            cmd.append("--previous")
        
        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")
    
    def exec(
        self,
        pod_name: str,
        command: List[str],
        namespace: Optional[str] = None,
        container: Optional[str] = None
    ) -> str:
        """kubectl exec"""
        cmd = ["exec", pod_name, "--"]
        
        if container:
            cmd.extend(["-c", container])
        
        cmd.extend(command)
        
        result = self.run(cmd, namespace=namespace, output_format=None)
        return result.get("stdout", "")


# Global instance
kubectl = KubectlWrapper()
```

**Пріоритет:** 🟡 СЕРЕДНІЙ

---

### 6️⃣ **`api/main.py`** - FastAPI app

**Що додати:**

```python
# api/main.py

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from config.settings import settings
from utils.logger import logger
from api.routes import diagnose, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info(f"🚀 Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Ollama URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"EKS Cluster: {settings.EKS_CLUSTER_NAME}")
    
    # Check Ollama health
    from llm.ollama_client import get_ollama_client
    client = get_ollama_client()
    
    if not client.health_check():
        logger.warning("⚠️ Ollama не доступний! Перевірте чи запущений: ollama serve")
    else:
        logger.info("✅ Ollama підключений")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down")


# Create app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
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
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
```

**Пріоритет:** 🔥 ВИСОКИЙ

---

### 7️⃣ **`api/routes/health.py`** - Health check endpoint

```python
# api/routes/health.py

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
    except:
        pass
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "components": {
            "ollama": ollama_status,
            "kubectl": kubectl_status
        },
        "config": {
            "model": settings.OLLAMA_MODEL,
            "eks_cluster": settings.EKS_CLUSTER_NAME,
            "language": settings.DEFAULT_LANGUAGE
        }
    }
```

**Пріоритет:** 🟢 НИЗЬКИЙ (але корисно для моніторингу)

---

### 8️⃣ **`api/routes/diagnose.py`** - Головний endpoint діагностики

```python
# api/routes/diagnose.py

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
        logger.info(f"Отримано запит на діагностику: {request.message[:50]}...")
        
        # Конвертувати language string → enum
        lang = Language.UKRAINIAN if request.language == "uk" else Language.ENGLISH
        
        # Створити diagnostic request
        diag_req = DiagnosticRequest(
            user_message=request.message,
            resource_type=request.resource_type,
            namespace=request.namespace,
            kubectl_output=request.kubectl_output,
            language=lang,
            eks_context={
                "cluster_name": "prod-cluster",  # TODO: from settings
                "region": "eu-west-1",
                "k8s_version": "1.28"
            }
        )
        
        # Виконати діагностику
        response = orchestrator.diagnose(diag_req)
        
        return DiagnoseResponse(
            diagnosis=response.text,
            model=response.model,
            generation_time=response.generation_time,
            tokens_generated=response.tokens_generated
        )
    
    except Exception as e:
        logger.error(f"Помилка діагностики: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/diagnose/stream")
async def diagnose_stream(request: DiagnoseRequest):
    """Streaming діагностика (SSE)"""
    # TODO: Implement streaming
    raise HTTPException(status_code=501, detail="Streaming not implemented yet")
```

**Пріоритет:** 🔥 КРИТИЧНИЙ

---

### 9️⃣ **`api/models/request.py`** & **`response.py`** - Pydantic schemas

```python
# api/models/request.py

from pydantic import BaseModel, Field
from typing import Optional


class DiagnoseRequest(BaseModel):
    """Запит на діагностику"""
    message: str = Field(..., description="Опис проблеми українською")
    resource_type: Optional[str] = Field(None, description="Тип ресурсу (pod, service, node)")
    namespace: str = Field(default="default", description="Kubernetes namespace")
    kubectl_output: Optional[str] = Field(None, description="Вивід kubectl команд")
    language: str = Field(default="uk", description="Мова відповіді (uk або en)")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "Мій под в CrashLoopBackOff, що робити?",
                "resource_type": "pod",
                "namespace": "production"
            }
        }
```

```python
# api/models/response.py

from pydantic import BaseModel
from typing import Optional, Dict, Any


class DiagnoseResponse(BaseModel):
    """Відповідь з діагнозом"""
    diagnosis: str
    model: str
    generation_time: float
    tokens_generated: int
    cached: bool = False
    
    class Config:
        schema_extra = {
            "example": {
                "diagnosis": "## 1. Швидке резюме\nПод крашиться через...",
                "model": "llama3.2:3b-instruct",
                "generation_time": 12.5,
                "tokens_generated": 450,
                "cached": False
            }
        }
```

**Пріоритет:** 🟡 СЕРЕДНІЙ

---

## 🧪 ТЕСТИ

### 10️⃣ **`tests/test_prompts.py`**

```python
# tests/test_prompts.py

import pytest
from prompts.multilang_prompts import (
    prompt_manager,
    Language,
    detect_language
)


def test_detect_ukrainian_language():
    """Тест визначення української мови"""
    text = "Мій под не запускається"
    lang = detect_language(text)
    assert lang == Language.UKRAINIAN


def test_detect_english_language():
    """Тест визначення англійської"""
    text = "My pod is not starting"
    lang = detect_language(text)
    assert lang == Language.ENGLISH


def test_build_prompt_ukrainian():
    """Тест генерації українського промпта"""
    prompt = prompt_manager.build_full_prompt(
        user_message="Тестове питання",
        resource_type="pod",
        language=Language.UKRAINIAN
    )
    
    assert "Ти експертний SRE" in prompt
    assert "Pod-Specific" in prompt


def test_get_system_prompt():
    """Тест базового system prompt"""
    prompt = prompt_manager.get_system_prompt(
        language=Language.UKRAINIAN,
        include_cloud=True
    )
    
    assert "AWS EKS" in prompt
    assert len(prompt) > 1000
```

**Запуск:** `pytest tests/test_prompts.py`

---

### 11️⃣ **`tests/test_llm.py`**

```python
# tests/test_llm.py

import pytest
from llm.ollama_client import get_ollama_client


@pytest.fixture
def ollama_client():
    return get_ollama_client()


def test_ollama_health(ollama_client):
    """Тест підключення до Ollama"""
    assert ollama_client.health_check() == True


def test_llm_generation(ollama_client):
    """Тест генерації"""
    response = ollama_client.generate(
        prompt="What is Kubernetes?",
        max_tokens=50
    )
    
    assert response.text
    assert len(response.text) > 10
    assert response.tokens_generated > 0


def test_list_models(ollama_client):
    """Тест списку моделей"""
    models = ollama_client.list_models()
    assert isinstance(models, list)
    assert len(models) > 0
```

**Запуск:** `pytest tests/test_llm.py` (потребує запущений Ollama)

---

## 📊 ПРІОРИТЕТИ ІМПЛЕМЕНТАЦІЇ

### Фаза 1: Базовий функціонал (1-2 дні) 🔥
1. ✅ `config/settings.py` - конфігурація
2. ✅ `utils/logger.py` - логування
3. ✅ `llm/ollama_client.py` - LLM client
4. ✅ `llm/prompt_manager.py` - orchestration
5. ✅ Скопіювати готові файли з artifacts

### Фаза 2: API (1 день) 🟡
6. ✅ `api/main.py` - FastAPI app
7. ✅ `api/routes/diagnose.py` - головний endpoint
8. ✅ `api/routes/health.py` - health check
9. ✅ `api/models/` - Pydantic schemas

### Фаза 3: K8s Integration (1-2 дні) 🟢
10. ✅ `k8s/kubectl_wrapper.py` - generic kubectl
11. ✅ Тестування з реальним EKS кластером
12. ✅ Емуляція проблем

### Фаза 4: Тести (1 день) 🔵
13. ✅ `tests/test_prompts.py`
14. ✅ `tests/test_llm.py`
15. ✅ `tests/test_api.py`

---

## 🚀 ШВИДКИЙ СТАРТ (Наступні кроки)

### 1. Заповнити критичні файли:

```bash
# 1. Settings
nano config/settings.py
# Скопіювати код з цього документа

# 2. Logger
nano utils/logger.py

# 3. Ollama Client
nano llm/ollama_client.py

# 4. Prompt Manager
nano llm/prompt_manager.py

# 5. FastAPI Main
nano api/main.py

# 6. Diagnose route
nano api/routes/diagnose.py
```

### 2. Оновити requirements.txt:

```txt
# Додати якщо немає:
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
loguru==0.7.2
```

### 3. Встановити залежності на Jetson:

```bash
cd ~/k8s-llm-admin
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Створити .env:

```bash
cat > .env << 'EOF'
# LLM
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b-instruct

# AWS
AWS_REGION=eu-west-1
EKS_CLUSTER_NAME=your-cluster-name

# Language
DEFAULT_LANGUAGE=uk

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true
LOG_LEVEL=INFO
EOF
```

### 5. Запустити API:

```bash
# Термінал 1: Ollama
ollama serve

# Термінал 2: API
python api/main.py
```

### 6. Тест:

```bash
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій под в CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default"
  }'
```

---

## ✅ Checklist завершення Кроку 1

```
[ ] config/settings.py заповнений
[ ] utils/logger.py працює
[ ] llm/ollama_client.py готовий
[ ] llm/prompt_manager.py реалізований
[ ] api/main.py створений
[ ] api/routes/diagnose.py працює
[ ] api/routes/health.py готовий
[ ] .env файл налаштований
[ ] Ollama запущений на Jetson
[ ] API стартує без помилок
[ ] Health check повертає 200
[ ] Тестовий запит працює
[ ] Відповідь українською
[ ] Логи записуються
```

---

**Після завершення Кроку 1** переходимо до **Кроку 2: RAG система** (векторна БД, knowledge base, retrieval)!

Готові почати заповнювати файли? Який файл почнемо першим?