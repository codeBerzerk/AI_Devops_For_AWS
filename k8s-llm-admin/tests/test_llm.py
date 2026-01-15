import pytest

from llm.ollama_client import get_ollama_client


@pytest.fixture
def ollama_client():
    return get_ollama_client()


def test_ollama_health(ollama_client):
    """Тест підключення до Ollama"""
    assert ollama_client.health_check() is True


def test_llm_generation(ollama_client):
    """Тест генерації"""
    response = ollama_client.generate(
        prompt="What is Kubernetes?",
        max_tokens=50,
    )

    assert response.text
    assert len(response.text) > 10
    assert response.tokens_generated > 0


def test_list_models(ollama_client):
    """Тест списку моделей"""
    models = ollama_client.list_models()
    assert isinstance(models, list)
    assert len(models) > 0

