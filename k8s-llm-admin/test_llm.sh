#!/bin/bash
# Приклад тестування LLM через API

# Перевірка чи встановлений jq, якщо ні - використовуємо python для форматування JSON
if command -v jq &> /dev/null; then
    JSON_FORMATTER="jq ."
elif command -v python3 &> /dev/null; then
    JSON_FORMATTER="python3 -m json.tool"
else
    JSON_FORMATTER="cat"  # Просто виводимо як є
fi

echo "🧪 Тестування K8s LLM Admin API"
echo "================================"
echo ""

# 1. Health check
echo "1️⃣ Health Check:"
echo "---"
curl -s http://localhost:8000/api/health | $JSON_FORMATTER
echo ""
echo ""

# 2. Простий запит на діагностику
echo "2️⃣ Тест діагностики (простий запит):"
echo "---"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій pod в стані CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default",
    "language": "uk"
  }')

echo "$RESPONSE" | $JSON_FORMATTER
echo ""
echo ""

# 3. Запит з kubectl output
echo "3️⃣ Тест діагностики (з kubectl output):"
echo "---"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Подивись на цей вивід kubectl і скажи що не так",
    "resource_type": "pod",
    "namespace": "default",
    "kubectl_output": "NAME: my-app-7d8b49557f-xyz\nSTATUS: CrashLoopBackOff\nRESTARTS: 12\nEVENTS:\n  Warning  Failed  2m ago  Error: ImagePullBackOff",
    "language": "uk"
  }')

echo "$RESPONSE" | $JSON_FORMATTER
echo ""
echo ""

# 4. Network проблема
echo "4️⃣ Тест мережевої проблеми:"
echo "---"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій Service недоступний ззовні, що перевірити?",
    "resource_type": "network",
    "namespace": "default",
    "language": "uk"
  }')

echo "$RESPONSE" | $JSON_FORMATTER
echo ""
echo ""

echo "✅ Тестування завершено!"
echo ""
echo "💡 Порада: Встанови jq для кращого форматування JSON:"
echo "   sudo apt-get install jq"
