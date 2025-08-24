#!/bin/bash

# Скрипт для управления Docker-контейнерами бота скальпинга
# Использование: ./docker-manager.sh [build|start|stop|restart|logs|status|clean|shell]

COMPOSE_FILE="docker-compose.yml"
SERVICE_NAME="scalping-bot"

case "$1" in
    build)
        echo "🔨 Сборка Docker образа..."
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        if [ $? -eq 0 ]; then
            echo "✅ Образ успешно собран"
        else
            echo "❌ Ошибка при сборке образа"
            exit 1
        fi
        ;;
        
    start)
        echo "🚀 Запуск Docker контейнеров..."
        
        # Проверяем, существует ли .env файл
        if [ ! -f ".env" ]; then
            echo "⚠️ Файл .env не найден"
            echo "Создайте .env файл с вашими настройками или запустите:"
            echo "python3 quick_setup.py"
            exit 1
        fi
        
        # Создаем директорию для логов
        mkdir -p logs
        
        # Запускаем контейнеры
        docker-compose -f "$COMPOSE_FILE" up -d
        
        if [ $? -eq 0 ]; then
            echo "✅ Контейнеры запущены"
            echo "📊 Статус:"
            docker-compose -f "$COMPOSE_FILE" ps
        else
            echo "❌ Ошибка при запуске контейнеров"
            exit 1
        fi
        ;;
        
    stop)
        echo "🛑 Остановка Docker контейнеров..."
        docker-compose -f "$COMPOSE_FILE" down
        
        if [ $? -eq 0 ]; then
            echo "✅ Контейнеры остановлены"
        else
            echo "❌ Ошибка при остановке контейнеров"
            exit 1
        fi
        ;;
        
    restart)
        echo "🔄 Перезапуск Docker контейнеров..."
        docker-compose -f "$COMPOSE_FILE" restart
        
        if [ $? -eq 0 ]; then
            echo "✅ Контейнеры перезапущены"
        else
            echo "❌ Ошибка при перезапуске контейнеров"
            exit 1
        fi
        ;;
        
    logs)
        echo "📋 Показ логов контейнера $SERVICE_NAME..."
        docker-compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
        ;;
        
    status)
        echo "📊 Статус Docker контейнеров..."
        docker-compose -f "$COMPOSE_FILE" ps
        
        echo ""
        echo "🔍 Детальная информация:"
        docker-compose -f "$COMPOSE_FILE" top
        
        echo ""
        echo "💾 Использование ресурсов:"
        docker stats --no-stream
        ;;
        
    shell)
        echo "🐚 Подключение к контейнеру $SERVICE_NAME..."
        docker-compose -f "$COMPOSE_FILE" exec "$SERVICE_NAME" /bin/bash
        ;;
        
    clean)
        echo "🧹 Очистка Docker ресурсов..."
        
        read -p "⚠️ Это удалит все контейнеры, образы и volumes. Продолжить? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "🛑 Останавливаем контейнеры..."
            docker-compose -f "$COMPOSE_FILE" down -v
            
            echo "🗑️ Удаляем образы..."
            docker rmi $(docker images -q scalping-bot) 2>/dev/null || true
            
            echo "🧹 Очищаем неиспользуемые ресурсы..."
            docker system prune -f
            
            echo "✅ Очистка завершена"
        else
            echo "❌ Очистка отменена"
        fi
        ;;
        
    update)
        echo "🔄 Обновление бота..."
        
        # Останавливаем контейнеры
        docker-compose -f "$COMPOSE_FILE" down
        
        # Обновляем код
        git pull origin main
        
        # Пересобираем образ
        docker-compose -f "$COMPOSE_FILE" build --no-cache
        
        # Запускаем заново
        docker-compose -f "$COMPOSE_FILE" up -d
        
        echo "✅ Обновление завершено"
        ;;
        
    monitor)
        echo "📊 Запуск мониторинга..."
        
        # Проверяем, запущен ли мониторинг
        if docker-compose -f "$COMPOSE_FILE" ps bot-monitor | grep -q "Up"; then
            echo "✅ Мониторинг уже запущен"
            echo "🌐 Откройте http://localhost:8080 в браузере"
        else
            echo "🚀 Запускаем мониторинг..."
            docker-compose -f "$COMPOSE_FILE" up -d bot-monitor
            echo "✅ Мониторинг запущен"
            echo "🌐 Откройте http://localhost:8080 в браузере"
        fi
        ;;
        
    *)
        echo "Использование: $0 {build|start|stop|restart|logs|status|shell|clean|update|monitor}"
        echo ""
        echo "Команды:"
        echo "  build   - Собрать Docker образ"
        echo "  start   - Запустить контейнеры"
        echo "  stop    - Остановить контейнеры"
        echo "  restart - Перезапустить контейнеры"
        echo "  logs    - Показать логи"
        echo "  status  - Показать статус"
        echo "  shell   - Подключиться к контейнеру"
        echo "  clean   - Очистить все Docker ресурсы"
        echo "  update  - Обновить код и пересобрать"
        echo "  monitor - Запустить веб-мониторинг"
        echo ""
        echo "Примеры:"
        echo "  ./docker-manager.sh build    # Собрать образ"
        echo "  ./docker-manager.sh start    # Запустить бота"
        echo "  ./docker-manager.sh logs     # Показать логи"
        echo "  ./docker-manager.sh status   # Показать статус"
        exit 1
        ;;
esac
