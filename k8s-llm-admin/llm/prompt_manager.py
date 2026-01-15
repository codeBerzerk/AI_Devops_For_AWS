from typing import Dict, Optional, Any, List
from dataclasses import dataclass

from prompts.multilang_prompts import (
    prompt_manager,
    Language,
    detect_language,
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
    eks_context: Optional[Dict[str, Any]] = None


class PromptOrchestrator:
    """Оркестрація промптів та LLM"""

    def __init__(self) -> None:
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
            eks_context=request.eks_context,
        )

        logger.debug(f"Згенерований промпт (довжина: {len(full_prompt)} chars)")

        # 3. Відправити до LLM
        try:
            response = self.llm_client.generate(
                prompt=full_prompt,
                temperature=0.7,
                max_tokens=2000,
            )

            logger.info(
                f"LLM відповів за {response.generation_time:.2f}s, "
                f"згенеровано {response.tokens_generated} токенів",
            )

            return response

        except Exception as e:  # pragma: no cover - логування помилок
            logger.error(f"Помилка LLM генерації: {e}")
            raise

    def chat(
        self,
        messages: List[Dict[str, str]],
        language: Language = Language.UKRAINIAN,
    ) -> LLMResponse:
        """Multi-turn conversation"""

        # Додати system prompt
        system_prompt = self.prompt_manager.get_system_prompt(
            language=language,
            include_cloud=True,
        )

        messages_with_system: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ] + messages

        return self.llm_client.chat(messages_with_system)


# Global instance
orchestrator = PromptOrchestrator()

