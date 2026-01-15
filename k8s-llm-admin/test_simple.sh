#!/bin/bash
# Простий тест без jq (тільки curl)

echo "🧪 Простий тест K8s LLM Admin API"
echo "=================================="
echo ""

# Health check
echo "1. Health Check:"
curl -s http://localhost:8000/api/health
echo ""
echo ""

# Простий запит
echo "2. Тест діагностики:"
curl -s -X POST http://localhost:8000/api/diagnose \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій pod в стані CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default",
    "language": "uk"
  }'
echo ""
echo ""

echo "✅ Готово!"
echo ""
echo "💡 Для кращого форматування встанови jq: sudo apt-get install jq"
