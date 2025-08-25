#!/bin/bash

# Скрипт для деплоя бота на production сервере
# Использование: ./production-deploy.sh [install|update|restart|logs|status]

REPO_URL="https://github.com/DArkadich/skalping.git"
PROJECT_DIR="skalping"
DOCKER_COMPOSE_FILE="docker-compose.yml"

case "$1" in
    install)
        echo "🚀 Установка бота на production сервере..."
        
        # Проверяем Docker
        if ! command -v docker &> /dev/null; then
            echo "❌ Docker не установлен"
            echo "Установите Docker: https://docs.docker.com/engine/install/"
            exit 1
        fi
        
        if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
            echo "❌ Docker Compose не установлен"
            echo "Установите Docker Compose: https://docs.docker.com/compose/install/"
            exit 1
        fi
        
        # Проверяем, существует ли директория
        if [ -d "$PROJECT_DIR" ]; then
            echo "⚠️ Директория $PROJECT_DIR уже существует"
            read -p "Удалить и переустановить? (y/N): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -rf "$PROJECT_DIR"
            else
                echo "❌ Установка отменена"
                exit 1
            fi
        fi
        
        # Клонируем репозиторий
        echo "📥 Клонирование репозитория..."
        git clone "$REPO_URL" "$PROJECT_DIR"
        
        if [ $? -ne 0 ]; then
            echo "❌ Ошибка при клонировании"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        # Проверяем наличие .env файла
        if [ ! -f ".env" ]; then
            echo "⚠️ Файл .env не найден"
            echo "Создайте .env файл с вашими настройками Bybit API"
            echo "Пример содержимого:"
            echo "BYBIT_API_KEY=your_api_key_here"
            echo "BYBIT_SECRET_KEY=your_secret_key_here"
            echo "BYBIT_TESTNET=false"
            echo "SYMBOL=BTCUSDT"
            echo "QUANTITY=0.001"
            exit 1
        fi
        
        # Собираем Docker образ
        echo "🔨 Сборка Docker образа..."
        if docker compose version &> /dev/null; then
            docker compose build --no-cache
        else
            docker-compose build --no-cache
        fi
        
        if [ $? -ne 0 ]; then
            echo "❌ Ошибка при сборке образа"
            exit 1
        fi
        
        # Создаем директорию для логов
        mkdir -p logs
        
        # Запускаем контейнеры
        echo "🚀 Запуск контейнеров..."
        if docker compose version &> /dev/null; then
            docker compose up -d
        else
            docker-compose up -d
        fi
        
        if [ $? -eq 0 ]; then
            echo "✅ Установка завершена успешно!"
            echo "📋 Следующие шаги:"
            echo "   1. Проверьте статус: ./production-deploy.sh status"
            echo "   2. Просмотрите логи: ./production-deploy.sh logs"
            echo "   3. Веб-мониторинг: http://your-server-ip:8080"
        else
            echo "❌ Ошибка при запуске контейнеров"
            exit 1
        fi
        ;;
        
    update)
        echo "🔄 Обновление бота на production сервере..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            echo "Используйте: ./production-deploy.sh install"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        # Сохраняем текущие изменения (если есть)
        if [ -f ".env" ]; then
            echo "💾 Сохраняем конфигурацию..."
            cp .env ../.env.backup
        fi
        
        # Делаем pull
        echo "📥 Обновление кода..."
        git pull origin main
        
        if [ $? -ne 0 ]; then
            echo "❌ Ошибка при обновлении"
            exit 1
        fi
        
        # Восстанавливаем конфигурацию
        if [ -f "../.env.backup" ]; then
            echo "🔄 Восстанавливаем конфигурацию..."
            cp ../.env.backup .env
            rm ../.env.backup
        fi
        
        # Пересобираем образ
        echo "🔨 Пересборка образа..."
        if docker compose version &> /dev/null; then
            docker compose build --no-cache
        else
            docker-compose build --no-cache
        fi
        
        # Перезапускаем контейнеры
        echo "🔄 Перезапуск контейнеров..."
        if docker compose version &> /dev/null; then
            docker compose down && docker compose up -d
        else
            docker-compose down && docker-compose up -d
        fi
        
        echo "✅ Обновление завершено успешно!"
        ;;
        
    restart)
        echo "🔄 Перезапуск бота..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        if docker compose version &> /dev/null; then
            docker compose restart
        else
            docker-compose restart
        fi
        
        echo "✅ Бот перезапущен"
        ;;
        
    stop)
        echo "🛑 Остановка бота..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        if docker compose version &> /dev/null; then
            docker compose down
        else
            docker-compose down
        fi
        
        echo "✅ Бот остановлен"
        ;;
        
    logs)
        echo "📋 Логи бота..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        if docker compose version &> /dev/null; then
            docker compose logs -f scalping-bot
        else
            docker-compose logs -f scalping-bot
        fi
        ;;
        
    status)
        echo "📊 Статус бота..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        if docker compose version &> /dev/null; then
            docker compose ps
            echo ""
            echo "🔍 Детальная информация:"
            docker compose top
        else
            docker-compose ps
            echo ""
            echo "🔍 Детальная информация:"
            docker-compose top
        fi
        ;;
        
    *)
        echo "Использование: $0 {install|update|restart|stop|logs|status}"
        echo ""
        echo "Команды для production:"
        echo "  install - Первичная установка на сервере"
        echo "  update  - Обновление кода и пересборка"
        echo "  restart - Перезапуск контейнеров"
        echo "  stop    - Остановка бота"
        echo "  logs    - Просмотр логов"
        echo "  status  - Статус контейнеров"
        echo ""
        echo "Примеры:"
        echo "  ./production-deploy.sh install    # Первый раз на сервере"
        echo "  ./production-deploy.sh update     # Обновление"
        echo "  ./production-deploy.sh status     # Проверка статуса"
        exit 1
        ;;
esac
