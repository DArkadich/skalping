# 🔑 Настройка API ключей Bybit

## ❌ Проблема: "API key is invalid"

Это означает, что API ключи в файле `.env` неверные или не настроены.

## 📋 Пошаговая настройка:

### 1. **Получите API ключи на Bybit:**

1. Зайдите на [bybit.com](https://www.bybit.com/)
2. Войдите в аккаунт
3. Перейдите в **API Management**
4. Нажмите **Create New Key**
5. Выберите **System Generated** (рекомендуется)
6. Установите разрешения:
   - ✅ **Read** - для чтения данных
   - ✅ **Trade** - для торговли
   - ✅ **Transfer** - для перевода средств (опционально)
7. Нажмите **Submit**
8. **Скопируйте и сохраните:**
   - **API Key**
   - **Secret Key**

### 2. **Настройте .env файл:**

```bash
# Откройте .env файл
nano .env
```

**Замените эти строки:**
```env
# Было:
BYBIT_API_KEY=your_api_key_here
BYBIT_SECRET_KEY=your_secret_key_here

# Стало (пример):
BYBIT_API_KEY=ABC123DEF456GHI789
BYBIT_SECRET_KEY=xyz789abc123def456ghi789jkl012mno345
```

### 3. **Проверьте настройки:**

```env
# Bybit API настройки
BYBIT_API_KEY=ваш_реальный_api_ключ
BYBIT_SECRET_KEY=ваш_реальный_secret_ключ
BYBIT_TESTNET=true  # true для тестовой сети, false для основной

# Настройки торговли
SYMBOL=BTCUSDT
QUANTITY=0.001

# Настройки скальпинга
PROFIT_TARGET=0.002
STOP_LOSS=0.001
MAX_POSITIONS=3
```

### 4. **Перезапустите бота:**

```bash
# Остановите
docker compose down

# Запустите заново
docker compose up -d

# Проверьте логи
docker compose logs -f scalping-bot
```

## ⚠️ Важные моменты:

### **Тестовая сеть (BYBIT_TESTNET=true):**
- Используйте тестовые API ключи
- Получите их на [testnet.bybit.com](https://testnet.bybit.com/)
- Безопасно для тестирования

### **Основная сеть (BYBIT_TESTNET=false):**
- Используйте основные API ключи
- **ВНИМАНИЕ:** Реальные деньги!
- Начинайте с малых сумм

### **Проверка API ключей:**
```bash
# Тест подключения
curl -X GET "https://api-testnet.bybit.com/v5/account/wallet-balance" \
  -H "X-BAPI-API-KEY: ваш_api_ключ" \
  -H "X-BAPI-TIMESTAMP: $(date +%s)000" \
  -H "X-BAPI-SIGN: ваш_подпись"
```

## 🚨 Безопасность:

1. **Никогда не делитесь** API ключами
2. **Не коммитьте** .env файл в git
3. **Используйте тестовую сеть** для начала
4. **Ограничьте разрешения** API ключа
5. **Регулярно обновляйте** ключи

## 🔍 Отладка:

### **Проверьте логи:**
```bash
docker compose logs -f scalping-bot
```

### **Проверьте статус:**
```bash
docker compose ps
```

### **Проверьте .env файл:**
```bash
cat .env
```

---

**После правильной настройки API ключей бот должен успешно подключиться к Bybit! 🎯**
