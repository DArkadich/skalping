#!/bin/bash

# Скрипт для проверки и запуска Docker

echo "🔍 Проверка Docker..."

# Проверяем версию Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker установлен: $(docker --version)"
else
    echo "❌ Docker не установлен"
    echo "Установите Docker Desktop с https://www.docker.com/products/docker-desktop/"
    exit 1
fi

# Проверяем версию Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose установлен: $(docker-compose --version)"
elif docker compose version &> /dev/null; then
    echo "✅ Docker Compose (v2) доступен: $(docker compose version)"
else
    echo "❌ Docker Compose не установлен"
    exit 1
fi

# Проверяем, запущен ли Docker демон
if docker ps &> /dev/null; then
    echo "✅ Docker демон запущен"
    echo "🚀 Docker готов к работе!"
else
    echo "❌ Docker демон не запущен"
    echo ""
    echo "🔧 Решения:"
    echo "1. Запустите Docker Desktop приложение"
    echo "2. Или запустите Docker из командной строки:"
    echo "   open -a Docker"
    echo ""
    echo "3. Подождите, пока Docker полностью загрузится"
    echo "4. Проверьте статус: docker ps"
    echo ""
    echo "После запуска Docker попробуйте снова:"
    echo "./docker-manager.sh build"
    exit 1
fi

echo ""
echo "🎯 Теперь вы можете:"
echo "  ./docker-manager.sh build    # Собрать образ"
echo "  ./docker-manager.sh start    # Запустить бота"
echo "  ./docker-manager.sh status   # Проверить статус"
