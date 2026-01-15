#!/bin/bash
# Скрипт для перевірки Ollama та доступних моделей

echo "🔍 Перевірка Ollama"
echo "==================="
echo ""

# 1. Перевірка чи Ollama запущений
echo "1. Перевірка доступності Ollama:"
if curl -s http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama доступний"
    curl -s http://localhost:11434/api/version | python3 -m json.tool 2>/dev/null || curl -s http://localhost:11434/api/version
else
    echo "❌ Ollama не доступний на http://localhost:11434"
    echo "   Запусти: ollama serve"
    exit 1
fi
echo ""

# 2. Список доступних моделей
echo "2. Доступні моделі в Ollama:"
MODELS=$(curl -s http://localhost:11434/api/tags)
if command -v jq &> /dev/null; then
    echo "$MODELS" | jq -r '.models[]?.name' | sed 's/^/   - /'
else
    echo "$MODELS" | python3 -c "import sys, json; data=json.load(sys.stdin); [print(f'   - {m[\"name\"]}') for m in data.get('models', [])]" 2>/dev/null || echo "$MODELS"
fi
echo ""

# 3. Перевірка чи модель з settings доступна
echo "3. Перевірка моделі з налаштувань:"
if [ -f .env ]; then
    MODEL=$(grep OLLAMA_MODEL .env | cut -d'=' -f2 | tr -d '"' | tr -d "'" || echo "llama3.2:3b")
else
    MODEL="llama3.2:3b"
fi

echo "   Модель з налаштувань: $MODEL"

# Перевірка чи модель існує
if echo "$MODELS" | grep -q "$MODEL"; then
    echo "   ✅ Модель '$MODEL' знайдена"
else
    echo "   ⚠️  Модель '$MODEL' не знайдена в списку доступних"
    echo "   Доступні моделі вище. Оновіть .env файл:"
    echo "   echo 'OLLAMA_MODEL=назва_моделі' >> .env"
fi
echo ""

# 4. Тест генерації
echo "4. Тест генерації (якщо модель доступна):"
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d "{
    \"model\": \"$MODEL\",
    \"prompt\": \"Привіт, це тест\",
    \"stream\": false
  }" 2>&1)

if echo "$TEST_RESPONSE" | grep -q "error"; then
    echo "   ❌ Помилка:"
    echo "$TEST_RESPONSE" | python3 -m json.tool 2>/dev/null || echo "$TEST_RESPONSE"
else
    echo "   ✅ Генерація працює"
fi
echo ""

echo "✅ Перевірка завершена"
