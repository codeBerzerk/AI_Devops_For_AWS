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
        base_url: str = settings.OLLAMA_BASE_URL,
        model: str = settings.OLLAMA_MODEL,
        timeout: int = settings.OLLAMA_TIMEOUT,
        max_retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
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
            
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    error_msg = f"Модель '{self.model}' не знайдена. Перевірте чи модель встановлена: ollama list"
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e
                logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
                raise
            
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
                timeout=5,
            )
            return response.status_code == 200
        except:
            return False


# Singleton instance
_ollama_client: Optional[OllamaClient] = None


def get_ollama_client() -> OllamaClient:
    """Get global Ollama client instance"""
    global _ollama_client

    if _ollama_client is None:
        _ollama_client = OllamaClient(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=settings.OLLAMA_TIMEOUT,
        )

    return _ollama_client

