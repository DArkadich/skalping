#!/bin/bash

# Скрипт для деплоя бота на продакшене
# Использование: ./deploy.sh [install|update|full]

REPO_URL="https://github.com/DArkadich/skalping.git"
PROJECT_DIR="skalping"

case "$1" in
    install)
        echo "🚀 Первичная установка бота на продакшене..."
        
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
        
        # Устанавливаем зависимости
        echo "📦 Установка зависимостей..."
        pip install -r requirements.txt
        
        if [ $? -ne 0 ]; then
            echo "❌ Ошибка при установке зависимостей"
            exit 1
        fi
        
        # Делаем скрипты исполняемыми
        chmod +x run_bot.sh
        
        echo "✅ Установка завершена успешно!"
        echo "📋 Следующие шаги:"
        echo "   1. cd $PROJECT_DIR"
        echo "   2. python3 quick_setup.py"
        echo "   3. python3 test_bot.py"
        echo "   4. ./run_bot.sh start"
        ;;
        
    update)
        echo "🔄 Обновление существующего бота..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            echo "Используйте: ./deploy.sh install"
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
        
        # Обновляем зависимости
        echo "📦 Обновление зависимостей..."
        pip install -r requirements.txt
        
        # Делаем скрипты исполняемыми
        chmod +x run_bot.sh
        
        echo "✅ Обновление завершено успешно!"
        ;;
        
    full)
        echo "🔄 Полное обновление (сброс всех изменений)..."
        
        if [ ! -d "$PROJECT_DIR" ]; then
            echo "❌ Директория $PROJECT_DIR не найдена"
            echo "Используйте: ./deploy.sh install"
            exit 1
        fi
        
        cd "$PROJECT_DIR"
        
        # Сохраняем конфигурацию
        if [ -f ".env" ]; then
            echo "💾 Сохраняем конфигурацию..."
            cp .env ../.env.backup
        fi
        
        # Принудительный сброс
        echo "🔄 Принудительный сброс кода..."
        git fetch origin
        git reset --hard origin/main
        
        # Восстанавливаем конфигурацию
        if [ -f "../.env.backup" ]; then
            echo "🔄 Восстанавливаем конфигурацию..."
            cp ../.env.backup .env
            rm ../.env.backup
        fi
        
        # Обновляем зависимости
        echo "📦 Обновление зависимостей..."
        pip install -r requirements.txt
        
        # Делаем скрипты исполняемыми
        chmod +x run_bot.sh
        
        echo "✅ Полное обновление завершено!"
        ;;
        
    *)
        echo "Использование: $0 {install|update|full}"
        echo ""
        echo "Команды:"
        echo "  install - Первичная установка на продакшене"
        echo "  update  - Обновление существующего бота"
        echo "  full    - Полное обновление (сброс всех изменений)"
        echo ""
        echo "Примеры:"
        echo "  ./deploy.sh install    # Первый раз на сервере"
        echo "  ./deploy.sh update     # Обычное обновление"
        echo "  ./deploy.sh full       # Принудительное обновление"
        exit 1
        ;;
esac
