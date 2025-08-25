# 🚀 Простой деплой бота скальпинга

## 📋 Что нужно сделать на production сервере:

### 1. **Клонируем репозиторий:**
```bash
git clone https://github.com/DArkadich/skalping.git
cd skalping
```

### 2. **Создаем .env файл:**
```bash
# Копируем пример
cp env_example.txt .env

# Редактируем с вашими API ключами
nano .env
```

**Важно:** Замените в `.env` файле:
- `your_api_key_here` → ваш реальный API ключ Bybit
- `your_secret_key_here` → ваш реальный Secret ключ Bybit
- `BYBIT_TESTNET=false` → для production (true для тестов)

### 3. **Запускаем Docker контейнер:**
```bash
# Собираем образ
docker compose build

# Запускаем
docker compose up -d
```

### 4. **Проверяем статус:**
```bash
# Статус контейнеров
docker compose ps

# Логи бота
docker compose logs -f scalping-bot
```

## 🔄 Обновления:

```bash
# Останавливаем
docker compose down

# Обновляем код
git pull origin main

# Пересобираем и запускаем
docker compose build
docker compose up -d
```

## 🛑 Остановка:

```bash
docker compose down
```

## 📊 Мониторинг:

После запуска откройте http://your-server-ip:8080 для веб-интерфейса.

## ⚠️ Важно:

1. **API ключи** - всегда используйте реальные ключи Bybit
2. **Тестовая сеть** - начните с `BYBIT_TESTNET=true`
3. **Размер позиций** - начинайте с малых сумм
4. **Мониторинг** - регулярно проверяйте логи

---

**Всё просто: git clone → .env → docker compose up! 🎯**
