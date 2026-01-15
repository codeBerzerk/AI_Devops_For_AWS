"""
Налаштування проекту
Environment variables, constants, configuration
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


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
    LLM_CONTEXT_WINDOW: int = Field(default=8192, env="LLM_CONTEXT_WINDOW")
    
    # AWS EKS
    AWS_REGION: str = Field(default="eu-west-1", env="AWS_REGION")
    AWS_PROFILE: Optional[str] = Field(default=None, env="AWS_PROFILE")
    EKS_CLUSTER_NAME: str = Field(default="", env="EKS_CLUSTER_NAME")
    
    # Kubernetes
    KUBECONFIG_PATH: Optional[str] = Field(default=None, env="KUBECONFIG")
    DEFAULT_NAMESPACE: str = Field(default="default", env="K8S_NAMESPACE")
    K8S_TIMEOUT: int = Field(default=30, env="K8S_TIMEOUT")
    
    # Language
    DEFAULT_LANGUAGE: str = Field(default="uk", env="DEFAULT_LANGUAGE")
    
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
    LOG_FILE: Optional[Path] = Field(default=None, env="LOG_FILE") # Kept for backward compatibility if needed
    LOG_DIR: Path = Field(default=Path("./logs"), env="LOG_DIR")
    
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
    
# Specific logic for LOG_DIR from guide
settings.LOG_DIR.mkdir(parents=True, exist_ok=True)
