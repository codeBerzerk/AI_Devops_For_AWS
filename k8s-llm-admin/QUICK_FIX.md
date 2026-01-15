# 🔧 Швидке виправлення помилки 404

## Проблема
```
404 Client Error: Not Found for url: http://localhost:11434/api/generate
```

Це означає, що модель `llama3.2:3b-instruct` не знайдена в Ollama.

## Рішення

### Варіант 1: Встановити правильну модель через .env

1. Створи/оновіть `.env` файл:
```bash
cd ~/AI_Devops_For_AWS/k8s-llm-admin
echo "OLLAMA_MODEL=llama3.2:3b" >> .env
```

2. Перезапусти API:
```bash
# Ctrl+C щоб зупинити
python api/main.py
```

### Варіант 2: Перевірити які моделі доступні

```bash
# Перевірити доступні моделі
ollama list

# Або через API
curl http://localhost:11434/api/tags | python3 -m json.tool
```

### Варіант 3: Використати скрипт перевірки

```bash
chmod +x check_ollama.sh
./check_ollama.sh
```

## Після виправлення

Перевір що працює:
```bash
./test_llm.sh
```

Або простий тест:
```bash
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Тест",
    "language": "uk"
  }'
```
