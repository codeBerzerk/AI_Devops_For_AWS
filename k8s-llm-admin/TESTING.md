# 🧪 Тестування K8s LLM Admin

## Швидкий старт

### 1. Запустити API сервер

```bash
cd ~/AI_Devops_For_AWS/k8s-llm-admin
source venv/bin/activate
python api/main.py
```

API буде доступний на `http://localhost:8000`

### 2. Тестування через curl

#### Health Check
```bash
curl http://localhost:8000/api/health | jq .
```

#### Простий запит на діагностику
```bash
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій pod в стані CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default",
    "language": "uk"
  }' | jq .
```

#### Запит з kubectl output
```bash
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Подивись на цей вивід kubectl і скажи що не так",
    "resource_type": "pod",
    "namespace": "default",
    "kubectl_output": "NAME: my-app-7d8b49557f-xyz\nSTATUS: CrashLoopBackOff\nRESTARTS: 12",
    "language": "uk"
  }' | jq .
```

#### Мережева проблема
```bash
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій Service недоступний ззовні, що перевірити?",
    "resource_type": "network",
    "namespace": "default",
    "language": "uk"
  }' | jq .
```

### 3. Автоматичне тестування

```bash
chmod +x test_llm.sh
./test_llm.sh
```

## Тестування через Swagger UI

Відкрий браузер і перейди на:
```
http://localhost:8000/docs
```

Там можна:
- Побачити всі endpoints
- Протестувати API інтерактивно
- Подивитися схеми запитів/відповідей

## Приклади запитів

### Pod проблема
```json
{
  "message": "Мій pod постійно перезапускається, що робити?",
  "resource_type": "pod",
  "namespace": "production"
}
```

### Service проблема
```json
{
  "message": "Service не резолвиться через DNS",
  "resource_type": "network",
  "namespace": "default"
}
```

### З реальним kubectl output
```json
{
  "message": "Проаналізуй цей вивід і скажи що не так",
  "resource_type": "pod",
  "namespace": "default",
  "kubectl_output": "kubectl get pods -n default\nNAME: app-xyz\nSTATUS: ImagePullBackOff\n..."
}
```

## Очікувана відповідь

LLM повинен відповісти структуровано:

```json
{
  "diagnosis": "## 1. Швидке резюме\n...\n\n## 2. Аналіз проблеми\n...\n\n## 3. Основна причина\n...\n\n## 4. Діагностичні команди\n...\n\n## 5. Кроки вирішення\n...\n\n## 6. Перевірка\n...\n\n## 7. Профілактика\n...",
  "model": "llama3.2:3b-instruct",
  "generation_time": 12.5,
  "tokens_generated": 450
}
```

## Troubleshooting

### Ollama не доступний
```bash
# Перевірити чи запущений Ollama
curl http://localhost:11434/api/version

# Якщо ні, запустити:
ollama serve
```

### Помилка імпорту модулів
```bash
# Переконатися що в віртуальному середовищі
source venv/bin/activate

# Перевірити що всі залежності встановлені
pip install -r requirements.txt
```

### API не відповідає
```bash
# Перевірити логи
tail -f logs/app.log

# Перевірити чи API запущений
curl http://localhost:8000/
```
