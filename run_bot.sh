#!/bin/bash

# Скрипт для запуска бота скальпинга
# Использование: ./run_bot.sh [start|stop|status|test]

BOT_NAME="scalping_bot"
LOG_FILE="scalping_bot.log"
PID_FILE="bot.pid"

case "$1" in
    start)
        echo "🚀 Запуск бота скальпинга..."
        
        # Проверяем, не запущен ли уже бот
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "❌ Бот уже запущен с PID $PID"
                exit 1
            else
                echo "🧹 Удаляем устаревший PID файл"
                rm -f "$PID_FILE"
            fi
        fi
        
        # Запускаем бота в фоновом режиме
        nohup python3 main.py > "$LOG_FILE" 2>&1 &
        echo $! > "$PID_FILE"
        
        echo "✅ Бот запущен с PID $(cat $PID_FILE)"
        echo "📋 Логи: tail -f $LOG_FILE"
        echo "🛑 Остановка: ./run_bot.sh stop"
        ;;
        
    stop)
        echo "🛑 Остановка бота скальпинга..."
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "📴 Останавливаем процесс $PID..."
                kill $PID
                
                # Ждем завершения процесса
                for i in {1..10}; do
                    if ! ps -p $PID > /dev/null 2>&1; then
                        break
                    fi
                    echo "⏳ Ожидание завершения процесса... ($i/10)"
                    sleep 1
                done
                
                # Принудительно завершаем, если процесс не завершился
                if ps -p $PID > /dev/null 2>&1; then
                    echo "⚠️ Принудительное завершение процесса..."
                    kill -9 $PID
                fi
                
                rm -f "$PID_FILE"
                echo "✅ Бот остановлен"
            else
                echo "❌ Процесс $PID не найден"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ PID файл не найден"
        fi
        ;;
        
    status)
        echo "📊 Статус бота скальпинга..."
        
        if [ -f "$PID_FILE" ]; then
            PID=$(cat "$PID_FILE")
            if ps -p $PID > /dev/null 2>&1; then
                echo "✅ Бот запущен (PID: $PID)"
                echo "📋 Логи: $LOG_FILE"
                
                # Показываем последние строки лога
                if [ -f "$LOG_FILE" ]; then
                    echo ""
                    echo "📝 Последние записи в логе:"
                    tail -5 "$LOG_FILE"
                fi
            else
                echo "❌ Бот не запущен (PID файл устарел)"
                rm -f "$PID_FILE"
            fi
        else
            echo "❌ Бот не запущен"
        fi
        ;;
        
    test)
        echo "🧪 Запуск тестирования бота..."
        python3 test_bot.py
        ;;
        
    logs)
        echo "📋 Показ логов бота..."
        if [ -f "$LOG_FILE" ]; then
            tail -f "$LOG_FILE"
        else
            echo "❌ Файл логов не найден"
        fi
        ;;
        
    restart)
        echo "🔄 Перезапуск бота..."
        $0 stop
        sleep 2
        $0 start
        ;;
        
    *)
        echo "Использование: $0 {start|stop|status|test|logs|restart}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить бота"
        echo "  stop    - Остановить бота"
        echo "  status  - Показать статус"
        echo "  test    - Запустить тесты"
        echo "  logs    - Показать логи в реальном времени"
        echo "  restart - Перезапустить бота"
        exit 1
        ;;
esac
