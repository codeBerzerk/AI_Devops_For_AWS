# 🏗️ K8s LLM Admin - Повна структура Python проекту

## 📁 Структура файлів

```
k8s-llm-admin/
├── README.md                          # Документація проекту
├── requirements.txt                   # Python залежності
├── setup.py                          # Package setup
├── .env.example                      # Приклад environment variables
├── .gitignore                        # Git ignore file
│
├── config/                           # Конфігурація
│   ├── __init__.py
│   ├── settings.py                   # Головні налаштування
│   └── logging_config.py             # Logging setup
│
├── prompts/                          # Система промптів
│   ├── __init__.py
│   ├── system_prompts.py             # ВЖЕ СТВОРЕНИЙ ☑️
│   ├── templates.py                  # Jinja2 templates для промптів
│   └── validators.py                 # Валідація промптів
│
├── llm/                              # LLM взаємодія
│   ├── __init__.py
│   ├── ollama_client.py              # Ollama API client
│   ├── prompt_manager.py             # Управління промптами
│   ├── response_parser.py            # Парсинг відповідей LLM
│   └── cache.py                      # Кешування відповідей
│
├── k8s/                              # Kubernetes інтеграція
│   ├── __init__.py
│   ├── kubectl_wrapper.py            # Обгортка для kubectl
│   ├── resource_inspector.py         # Інспекція ресурсів
│   └── cluster_info.py               # Інформація про кластер
│
├── rag/                              # RAG система (Крок 2)
│   ├── __init__.py
│   ├── vector_store.py               # Векторна БД
│   ├── embeddings.py                 # Embedding генерація
│   ├── retriever.py                  # Пошук документів
│   └── knowledge_base/               # База знань
│       ├── k8s_docs/                 # K8s документація
│       ├── runbooks/                 # Runbooks
│       └── incidents/                # Історія інцидентів
│
├── api/                              # Backend API (Крок 3)
│   ├── __init__.py
│   ├── main.py                       # FastAPI app
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── diagnose.py               # Діагностика endpoints
│   │   ├── kubectl.py                # kubectl команди
│   │   └── health.py                 # Health checks
│   ├── models/
│   │   ├── __init__.py
│   │   ├── request.py                # Request schemas
│   │   └── response.py               # Response schemas
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py                   # Аутентифікація
│       └── rate_limit.py             # Rate limiting
│
├── utils/                            # Утиліти
│   ├── __init__.py
│   ├── logger.py                     # Logging helper
│   ├── metrics.py                    # Метрики
│   └── validators.py                 # Валідація input
│
├── tests/                            # Тести
│   ├── __init__.py
│   ├── test_prompts.py               # Тести промптів
│   ├── test_llm.py                   # Тести LLM
│   ├── test_k8s.py                   # Тести K8s
│   └── test_api.py                   # Тести API
│
├── scripts/                          # Допоміжні скрипти
│   ├── setup_jetson.sh               # Налаштування Jetson
│   ├── download_models.sh            # Завантаження моделей
│   └── benchmark.py                  # Benchmarking
│
├── docs/                             # Документація
│   ├── api.md                        # API документація
│   ├── prompts.md                    # Prompt engineering guide
│   ├── deployment.md                 # Deployment guide
│   └── examples/                     # Приклади використання
│
└── examples/                         # Приклади коду
    ├── simple_diagnostic.py
    ├── batch_analysis.py
    └── streaming_response.py
```

---

## 📝 Детальний опис кожного файлу

### 1. **prompts/system_prompts.py** ✅ ВЖЕ ГОТОВО

Див. попередній artifact - містить:
- Базові system prompts
- Спеціалізовані промпти (Pod, Network, Node, Deployment, Performance)
- Динамічна генерація промптів
- Few-shot examples
- Safety prompts
- Prompt optimization utilities

---

### 2. **prompts/templates.py**

```python
"""
Jinja2 templates для динамічної генерації промптів
Використовується для більш гнучкого template rendering
"""

from jinja2 import Environment, BaseLoader, Template
from typing import Dict, Any


# Template для базової діагностики
DIAGNOSTIC_TEMPLATE = """
{% if severity == "critical" %}
🚨 CRITICAL INCIDENT - IMMEDIATE ACTION REQUIRED
{% elif severity == "high" %}
⚠️ HIGH PRIORITY ISSUE
{% endif %}

# Kubernetes Issue Report

**Resource Type:** {{ resource_type }}
**Namespace:** {{ namespace }}
**Cluster:** {{ cluster_name }} ({{ k8s_version }})
**Reported:** {{ timestamp }}

## User Description:
{{ issue_description }}

{% if kubectl_output %}
## Available Diagnostic Data:
```
{{ kubectl_output }}
```
{% endif %}

{% if recent_changes %}
## Recent Changes Detected:
{% for change in recent_changes %}
- {{ change.timestamp }}: {{ change.description }}
{% endfor %}
{% endif %}

{% if similar_incidents %}
## Similar Past Incidents:
{% for incident in similar_incidents %}
- [{{ incident.date }}] {{ incident.title }} - {{ incident.resolution_summary }}
{% endfor %}
{% endif %}

Now, provide a structured diagnostic response.
"""


# Template для follow-up питань
FOLLOWUP_TEMPLATE = """
# Conversation Context

## Previous Diagnosis:
{{ previous_diagnosis }}

## Actions Taken:
{% for action in actions_taken %}
{{ loop.index }}. {{ action.description }}
   Command: `{{ action.command }}`
   Result: {{ action.result }}
{% endfor %}

## Current Situation:
{{ current_status }}

## New Information:
{{ new_info }}

## User Follow-up Question:
{{ user_question }}

Given this context, provide updated guidance. Don't repeat what's already been covered.
"""


# Template для multi-resource аналізу
MULTI_RESOURCE_TEMPLATE = """
# Multi-Resource Analysis Required

You are analyzing multiple Kubernetes resources together to diagnose a system-wide issue.

## Resources Involved:
{% for resource in resources %}
### {{ resource.type }}: {{ resource.name }}
**Status:** {{ resource.status }}
**Last Update:** {{ resource.last_update }}

{% if resource.logs %}
**Recent Logs:**
```
{{ resource.logs | truncate(500) }}
```
{% endif %}

{% if resource.events %}
**Events:**
{% for event in resource.events[-5:] %}
- {{ event.timestamp }}: {{ event.message }}
{% endfor %}
{% endif %}

---
{% endfor %}

## System-Wide Symptoms:
{{ system_symptoms }}

Analyze these resources holistically and identify cascading failures or root cause.
"""


class PromptTemplateManager:
    """Управління Jinja2 templates для промптів"""
    
    def __init__(self):
        self.env = Environment(loader=BaseLoader())
        self.env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s
    
    def render_diagnostic(self, context: Dict[str, Any]) -> str:
        """Рендер діагностичного промпта"""
        template = self.env.from_string(DIAGNOSTIC_TEMPLATE)
        return template.render(**context)
    
    def render_followup(self, context: Dict[str, Any]) -> str:
        """Рендер follow-up промпта"""
        template = self.env.from_string(FOLLOWUP_TEMPLATE)
        return template.render(**context)
    
    def render_multi_resource(self, context: Dict[str, Any]) -> str:
        """Рендер multi-resource аналізу"""
        template = self.env.from_string(MULTI_RESOURCE_TEMPLATE)
        return template.render(**context)
    
    def render_custom(self, template_str: str, context: Dict[str, Any]) -> str:
        """Рендер кастомного template"""
        template = self.env.from_string(template_str)
        return template.render(**context)
```

**Призначення:** Гнучке створення промптів з динамічними даними через Jinja2 templates.

---

### 3. **prompts/validators.py**

```python
"""
Валідація промптів перед відправкою до LLM
Перевірка безпеки, довжини, форматування
"""

import re
from typing import List, Tuple, Optional
from enum import Enum


class ValidationError(Exception):
    """Помилка валідації промпта"""
    pass


class SecurityLevel(Enum):
    """Рівні безпеки операцій"""
    SAFE = "safe"              # Тільки читання
    MODERATE = "moderate"      # Зміни з low impact
    DESTRUCTIVE = "destructive"  # Видалення, scale to 0, etc.


class PromptValidator:
    """Валідація промптів на безпеку та коректність"""
    
    # Небезпечні kubectl команди
    DESTRUCTIVE_COMMANDS = [
        r'kubectl\s+delete',
        r'kubectl\s+drain',
        r'kubectl\s+cordon',
        r'kubectl\s+taint.*NoSchedule',
        r'kubectl\s+scale.*--replicas=0',
        r'kubectl\s+patch.*delete',
    ]
    
    # Заборонені patterns в промптах
    FORBIDDEN_PATTERNS = [
        r'rm\s+-rf',
        r'sudo\s+rm',
        r'DROP\s+TABLE',
        r'DELETE\s+FROM.*WHERE\s+1=1',
        r'--force.*--grace-period=0',
    ]
    
    def __init__(self, max_prompt_length: int = 8000):
        self.max_length = max_prompt_length
    
    def validate_prompt(
        self, 
        prompt: str, 
        allow_destructive: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Валідація промпта
        
        Args:
            prompt: Промпт для перевірки
            allow_destructive: Чи дозволені деструктивні операції
        
        Returns:
            (is_valid, error_message)
        """
        # 1. Перевірка довжини
        if len(prompt) > self.max_length:
            return False, f"Prompt too long: {len(prompt)} > {self.max_length}"
        
        # 2. Перевірка на порожній промпт
        if not prompt.strip():
            return False, "Empty prompt"
        
        # 3. Перевірка на заборонені patterns
        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return False, f"Forbidden pattern detected: {pattern}"
        
        # 4. Перевірка на деструктивні команди
        if not allow_destructive:
            for pattern in self.DESTRUCTIVE_COMMANDS:
                if re.search(pattern, prompt, re.IGNORECASE):
                    return False, f"Destructive command detected: {pattern}. Set allow_destructive=True if intentional."
        
        # 5. Перевірка на injection attacks
        if self._check_injection(prompt):
            return False, "Potential injection attack detected"
        
        return True, None
    
    def _check_injection(self, prompt: str) -> bool:
        """Перевірка на prompt injection спроби"""
        injection_indicators = [
            "ignore previous instructions",
            "disregard all prior",
            "new instructions:",
            "system: you are now",
            "forget everything above",
        ]
        
        prompt_lower = prompt.lower()
        return any(indicator in prompt_lower for indicator in injection_indicators)
    
    def classify_security_level(self, prompt: str) -> SecurityLevel:
        """Класифікація рівня безпеки операції"""
        # Деструктивні операції
        for pattern in self.DESTRUCTIVE_COMMANDS:
            if re.search(pattern, prompt, re.IGNORECASE):
                return SecurityLevel.DESTRUCTIVE
        
        # Команди зміни стану
        moderate_patterns = [
            r'kubectl\s+apply',
            r'kubectl\s+patch',
            r'kubectl\s+scale',
            r'kubectl\s+rollout\s+restart',
        ]
        
        for pattern in moderate_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                return SecurityLevel.MODERATE
        
        # Безпечні операції (тільки читання)
        return SecurityLevel.SAFE
    
    def extract_kubectl_commands(self, prompt: str) -> List[str]:
        """Витягти всі kubectl команди з промпта"""
        # Regex для kubectl команд
        pattern = r'kubectl\s+[^\n]+'
        commands = re.findall(pattern, prompt)
        return [cmd.strip() for cmd in commands]
    
    def sanitize_sensitive_data(self, prompt: str) -> str:
        """Видалення чутливих даних з промпта перед логуванням"""
        # Маскування секретів
        prompt = re.sub(
            r'(password|token|secret|key)[\s:=]+[^\s]+',
            r'\1=***REDACTED***',
            prompt,
            flags=re.IGNORECASE
        )
        
        # Маскування IP адрес
        prompt = re.sub(
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            'XXX.XXX.XXX.XXX',
            prompt
        )
        
        return prompt


# Глобальний validator instance
validator = PromptValidator()
```

**Призначення:** Безпека - перевірка промптів на небезпечні команди, injection атаки, витік чутливих даних.

---

### 4. **llm/ollama_client.py**

```python
"""
Client для взаємодії з Ollama API
Обгортка для HTTP запитів з retry logic, streaming, caching
"""

import requests
import json
import time
from typing import Dict, Any, Optional, Generator, List
from dataclasses import dataclass
from enum import Enum

from config.settings import settings
from utils.logger import logger


class ModelSize(Enum):
    """Розміри моделей"""
    SMALL = "1-2B"    # DeepSeek Coder 1.3B
    MEDIUM = "3-4B"   # Llama 3.2 3B, Phi-3-mini
    LARGE = "7B+"     # CodeLlama 7B


@dataclass
class LLMResponse:
    """Структурована відповідь від LLM"""
    text: str
    model: str
    tokens_generated: int
    generation_time: float
    prompt_tokens: int
    cached: bool = False


class OllamaClient:
    """Client для Ollama API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:3b-instruct",
        timeout: int = 120,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Endpoints
        self.generate_url = f"{self.base_url}/api/generate"
        self.chat_url = f"{self.base_url}/api/chat"
        self.models_url = f"{self.base_url}/api/tags"
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        stream: bool = False
    ) -> LLMResponse | Generator[str, None, None]:
        """
        Генерація відповіді від LLM
        
        Args:
            prompt: User prompt
            system_prompt: System instructions
            temperature: Sampling temperature (0.0 - 1.0)
            max_tokens: Max tokens to generate
            stream: Whether to stream response
        
        Returns:
            LLMResponse або Generator для streaming
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        start_time = time.time()
        
        try:
            if stream:
                return self._generate_stream(payload)
            else:
                return self._generate_complete(payload, start_time)
        
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    def _generate_complete(self, payload: Dict, start_time: float) -> LLMResponse:
        """Повна генерація (non-streaming)"""
        response = self._make_request(self.generate_url, payload)
        
        generation_time = time.time() - start_time
        
        return LLMResponse(
            text=response.get('response', ''),
            model=self.model,
            tokens_generated=response.get('eval_count', 0),
            generation_time=generation_time,
            prompt_tokens=response.get('prompt_eval_count', 0)
        )
    
    def _generate_stream(self, payload: Dict) -> Generator[str, None, None]:
        """Streaming генерація"""
        response = requests.post(
            self.generate_url,
            json=payload,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line)
                if 'response' in chunk:
                    yield chunk['response']
                
                if chunk.get('done', False):
                    break
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> LLMResponse:
        """
        Chat completion (multi-turn conversation)
        
        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
        
        Returns:
            LLMResponse
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        start_time = time.time()
        response = self._make_request(self.chat_url, payload)
        generation_time = time.time() - start_time
        
        return LLMResponse(
            text=response['message']['content'],
            model=self.model,
            tokens_generated=response.get('eval_count', 0),
            generation_time=generation_time,
            prompt_tokens=response.get('prompt_eval_count', 0)
        )
    
    def _make_request(self, url: str, payload: Dict) -> Dict:
        """HTTP request з retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    timeout=self.timeout
                )
                response.raise_for_status()
                return response.json()
            
            except requests.exceptions.Timeout:
                logger.warning(f"Request timeout (attempt {attempt + 1}/{self.max_retries})")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                raise
    
    def list_models(self) -> List[str]:
        """Список доступних моделей"""
        response = requests.get(self.models_url, timeout=10)
        response.raise_for_status()
        models = response.json().get('models', [])
        return [m['name'] for m in models]
    
    def model_info(self, model_name: Optional[str] = None) -> Dict:
        """Інформація про модель"""
        model = model_name or self.model
        response = requests.post(
            f"{self.base_url}/api/show",
            json={"name": model},
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> bool:
        """Перевірка доступності Ollama"""
        try:
            response = requests.get(
                f"{self.base_url}/api/version",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
```

**Призначення:** HTTP client для Ollama з streaming, retry logic, error handling.

---

### 5. **config/settings.py**

```python
"""
Налаштування проекту
Environment variables, constants, configuration
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Головні налаштування проекту"""
    
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
    LLM_CONTEXT_WINDOW: int = Field(default=8192, env="LLM_CONTEXT_WINDOW")
    
    # Kubernetes
    KUBECONFIG_PATH: Optional[str] = Field(default=None, env="KUBECONFIG")
    DEFAULT_NAMESPACE: str = Field(default="default", env="K8S_NAMESPACE")
    K8S_TIMEOUT: int = Field(default=30, env="K8S_TIMEOUT")
    
    # RAG (для Кроку 2)
    VECTOR_DB_PATH: Path = Field(default=Path("./data/vector_db"), env="VECTOR_DB_PATH")
    EMBEDDING_MODEL: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    TOP_K_RESULTS: int = Field(default=5, env="RAG_TOP_K")
    
    # API Server
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_WORKERS: int = Field(default=1, env="API_WORKERS")
    CORS_ORIGINS: list = Field(default=["*"], env="CORS_ORIGINS")
    
    # Security
    API_KEY: Optional[str] = Field(default=None, env="API_KEY")
    RATE_LIMIT_PER_MINUTE: int = Field(default=30, env="RATE_LIMIT")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FILE: Optional[Path] = Field(default=None, env="LOG_FILE")
    
    # Cache
    ENABLE_CACHE: bool = Field(default=True, env="ENABLE_CACHE")
    CACHE_TTL_SECONDS: int = Field(default=3600, env="CACHE_TTL")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Глобальний settings instance
settings = Settings()


# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "rag" / "knowledge_base"

# Створення директорій
for dir_path in [DATA_DIR, LOGS_DIR, KNOWLEDGE_BASE_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)
```

**Призначення:** Централізована конфігурація через environment variables з Pydantic validation.

---

## 🚀 Команди для створення проекту

### 1. Створіть структуру на вашому комп'ютері:

```bash
# Створити проект
mkdir -p k8s-llm-admin
cd k8s-llm-admin

# Git init
git init
echo "# K8s LLM Admin Assistant" > README.md

# Створити структуру директорій
mkdir -p config prompts llm k8s rag api/routes api/models api/middleware utils tests scripts docs examples

# Створити __init__.py файли
find . -type d -exec touch {}/__init__.py \;

# .gitignore
cat > .gitignore << 'EOF'
__pycache__/
*.py[cod]
*$py.class
.env
.venv/
venv/
*.log
.DS_Store
data/
logs/
*.swp
.idea/
.vscode/
EOF
```

### 2. requirements.txt:

```txt
# LLM
requests==2.31.0

# API
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-multipart==0.0.6

# Kubernetes
kubernetes==28.1.0
pyyaml==6.0.1

# RAG (Крок 2)
chromadb==0.4.18
sentence-transformers==2.2.2
langchain==0.0.340

# Templates
jinja2==3.1.2

# Utilities
python-dotenv==1.0.0
aiohttp==3.9.1
httpx==0.25.2

# Logging & Monitoring
loguru==0.7.2
prometheus-client==0.19.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2

# Dev tools
black==23.11.0
flake8==6.1.0
mypy==1.7.1
```

### 3. .env.example:

```bash
# LLM Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b-instruct
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# Kubernetes
KUBECONFIG=/path/to/kubeconfig
K8S_NAMESPACE=default

# API
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false

# Security
API_KEY=your-secret-key-here
RATE_LIMIT=30

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Cache
ENABLE_CACHE=true
CACHE_TTL=3600
```

---

## 📦 Встановлення на Jetson

### Git push і pull:

```bash
# На вашому комп'ютері
git add .
git commit -m "Initial project structure"
git remote add origin https://github.com/your-username/k8s-llm-admin.git
git push -u origin main

# На Jetson
cd ~
git clone https://github.com/your-username/k8s-llm-admin.git
cd k8s-llm-admin

# Віртуальне середовище
python3 -m venv venv
source venv/bin/activate

# Залежності
pip install --upgrade pip
pip install -r requirements.txt

# .env файл
cp .env.example .env
nano .env  # Відредагувати налаштування

# Тест
python -m pytest tests/
```

---

## ✅ Checklist створення проекту

```
[ ] Структура директорій створена
[ ] __init__.py файли в кожній папці
[ ] .gitignore налаштований
[ ] requirements.txt створений
[ ] .env.example створений
[ ] Git repository ініціалізований
[ ] prompts/system_prompts.py скопійований з artifact
[ ] prompts/templates.py створений
[ ] prompts/validators.py створений
[ ] llm/ollama_client.py створений
[ ] config/settings.py створений
[ ] README.md з документацією
[ ] Git push на GitHub
[ ] Git clone на Jetson
[ ] Virtual environment на Jetson
[ ] Dependencies встановлені
[ ] Ollama запущений на Jetson
[ ] Базовий тест пройшов
```

---