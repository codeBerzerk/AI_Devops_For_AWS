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
