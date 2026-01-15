#!/bin/bash
# Тест streaming endpoint

echo "🧪 Тест Streaming API"
echo "===================="
echo ""

echo "1. Простий streaming запит:"
echo "---"
curl -N -X POST http://localhost:8000/api/diagnose/stream \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Мій pod в стані CrashLoopBackOff, що робити?",
    "resource_type": "pod",
    "namespace": "default",
    "language": "uk"
  }'
echo ""
echo ""

echo "✅ Тест завершено!"
echo ""
echo "💡 Для інтерактивного використання:"
echo "   python cli.py"
