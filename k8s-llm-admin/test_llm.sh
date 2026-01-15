#!/bin/bash
# Приклад тестування LLM через API

echo "🧪 Тестування K8s LLM Admin API"
echo "================================"
echo ""

# 1. Health check
echo "1️⃣ Health Check:"
curl -s http://localhost:8000/api/health | jq .
echo ""
echo ""

# 2. Простий запит на діагностику
echo "2️⃣ Тест діагностики (простий запит):"
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій pod в стані CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default",
    "language": "uk"
  }' | jq .
echo ""
echo ""

# 3. Запит з kubectl output
echo "3️⃣ Тест діагностики (з kubectl output):"
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Подивись на цей вивід kubectl і скажи що не так",
    "resource_type": "pod",
    "namespace": "default",
    "kubectl_output": "NAME: my-app-7d8b49557f-xyz\nSTATUS: CrashLoopBackOff\nRESTARTS: 12\nEVENTS:\n  Warning  Failed  2m ago  Error: ImagePullBackOff",
    "language": "uk"
  }' | jq .
echo ""
echo ""

# 4. Network проблема
echo "4️⃣ Тест мережевої проблеми:"
curl -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій Service недоступний ззовні, що перевірити?",
    "resource_type": "network",
    "namespace": "default",
    "language": "uk"
  }' | jq .
echo ""
echo ""

echo "✅ Тестування завершено!"
