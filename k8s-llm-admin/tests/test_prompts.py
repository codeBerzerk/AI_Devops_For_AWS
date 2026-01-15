import pytest

from prompts.multilang_prompts import (
    prompt_manager,
    Language,
    detect_language,
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
        language=Language.UKRAINIAN,
    )

    assert "Ти експертний SRE" in prompt
    assert "Pod-Specific" in prompt


def test_get_system_prompt():
    """Тест базового system prompt"""
    prompt = prompt_manager.get_system_prompt(
        language=Language.UKRAINIAN,
        include_cloud=True,
    )

    assert "AWS EKS" in prompt
    assert len(prompt) > 1000

