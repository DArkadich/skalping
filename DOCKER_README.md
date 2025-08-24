# 🐳 Docker для бота скальпинга

Этот документ описывает, как запустить бота для скальпинга в Docker-контейнерах.

## 🚀 Быстрый старт

### 1. **Убедитесь, что Docker установлен:**
```bash
docker --version
docker-compose --version
```

### 2. **Клонируйте репозиторий:**
```bash
git clone https://github.com/DArkadich/skalping.git
cd skalping
```

### 3. **Настройте конфигурацию:**
```bash
python3 quick_setup.py
```

### 4. **Запустите в Docker:**
```bash
./docker-manager.sh start
```

## 📋 Команды Docker-менеджера

### **Основные команды:**
```bash
./docker-manager.sh build    # Собрать образ
./docker-manager.sh start    # Запустить контейнеры
./docker-manager.sh stop     # Остановить контейнеры
./docker-manager.sh restart  # Перезапустить контейнеры
./docker-manager.sh logs     # Показать логи
./docker-manager.sh status   # Показать статус
./docker-manager.sh shell    # Подключиться к контейнеру
./docker-manager.sh clean    # Очистить все ресурсы
./docker-manager.sh update   # Обновить код и пересобрать
./docker-manager.sh monitor  # Запустить веб-мониторинг
```

### **Альтернативные команды Docker Compose:**
```bash
# Сборка и запуск
docker-compose up -d --build

# Просмотр логов
docker-compose logs -f scalping-bot

# Остановка
docker-compose down

# Перезапуск
docker-compose restart scalping-bot
```

## 🏗️ Архитектура

### **Сервисы:**
1. **`scalping-bot`** - Основной бот для скальпинга
2. **`bot-monitor`** - Веб-интерфейс для мониторинга (опционально)

### **Сети:**
- **`bot-network`** - Изолированная сеть для контейнеров

### **Volumes:**
- **`./logs:/app/logs`** - Логи бота
- **`./.env:/app/.env:ro`** - Конфигурация (только чтение)

## 🔧 Настройка

### **Переменные окружения:**
Все настройки передаются через файл `.env`:

```env
# Bybit API
BYBIT_API_KEY=your_api_key
BYBIT_SECRET_KEY=your_secret_key
BYBIT_TESTNET=true

# Торговые настройки
SYMBOL=BTCUSDT
QUANTITY=0.001
PROFIT_TARGET=0.002
STOP_LOSS=0.001
```

### **Порты:**
- **8080** - Веб-мониторинг (если включен)

## 📊 Мониторинг

### **Веб-интерфейс:**
```bash
./docker-manager.sh monitor
```
Откройте http://localhost:8080 в браузере

### **Логи в реальном времени:**
```bash
./docker-manager.sh logs
```

### **Статус контейнеров:**
```bash
./docker-manager.sh status
```

## 🛠️ Разработка

### **Подключение к контейнеру:**
```bash
./docker-manager.sh shell
```

### **Пересборка образа:**
```bash
./docker-manager.sh build
```

### **Обновление кода:**
```bash
./docker-manager.sh update
```

## 🔍 Отладка

### **Проверка логов:**
```bash
# Логи бота
docker-compose logs scalping-bot

# Логи мониторинга
docker-compose logs bot-monitor

# Все логи
docker-compose logs
```

### **Проверка статуса:**
```bash
# Статус контейнеров
docker-compose ps

# Использование ресурсов
docker stats

# Детальная информация
docker-compose top
```

### **Проверка сети:**
```bash
# Список сетей
docker network ls

# Информация о сети
docker network inspect skalping_bot-network
```

## 🧹 Очистка

### **Остановка и удаление:**
```bash
./docker-manager.sh clean
```

### **Ручная очистка:**
```bash
# Остановить контейнеры
docker-compose down

# Удалить образы
docker rmi scalping-skalping-bot

# Очистить неиспользуемые ресурсы
docker system prune -f
```

## ⚠️ Важные моменты

### **Безопасность:**
- Контейнеры запускаются от непривилегированного пользователя
- Файл `.env` монтируется только для чтения
- Сетевой доступ ограничен внутренней сетью

### **Производительность:**
- Используется Python 3.11 slim образ для меньшего размера
- Многоэтапная сборка для оптимизации
- Gzip сжатие для веб-интерфейса

### **Надежность:**
- Автоматический перезапуск при сбоях
- Health checks для мониторинга состояния
- Graceful shutdown для корректного завершения

## 🚨 Устранение неполадок

### **Проблемы с правами:**
```bash
# Сделать скрипты исполняемыми
chmod +x docker-manager.sh
chmod +x run_bot.sh
```

### **Проблемы с портами:**
```bash
# Проверить занятые порты
netstat -tulpn | grep :8080

# Изменить порт в docker-compose.yml
```

### **Проблемы с памятью:**
```bash
# Ограничить использование памяти
# В docker-compose.yml добавьте:
# deploy:
#   resources:
#     limits:
#       memory: 512M
```

### **Проблемы с сетью:**
```bash
# Пересоздать сеть
docker-compose down
docker network prune
docker-compose up -d
```

## 🔄 Обновления

### **Автоматическое обновление:**
```bash
./docker-manager.sh update
```

### **Ручное обновление:**
```bash
# Остановить контейнеры
docker-compose down

# Обновить код
git pull origin main

# Пересобрать и запустить
docker-compose up -d --build
```

## 📚 Дополнительные ресурсы

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Основной README](../README.md)
- [Быстрый старт](../QUICK_START.md)

---

**Удачного использования Docker! 🐳**
