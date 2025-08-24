#!/usr/bin/env python3
"""
Скрипт для быстрой настройки бота скальпинга
Интерактивно запрашивает необходимые параметры и создает .env файл
"""

import os
import sys

def get_input(prompt, default=None, required=True):
    """Получает ввод от пользователя с проверкой"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if user_input or not required:
            return user_input
        else:
            print("❌ Это поле обязательно для заполнения")

def create_env_file():
    """Создает .env файл с настройками"""
    print("🚀 Быстрая настройка бота скальпинга на Bybit")
    print("=" * 50)
    
    # Проверяем, существует ли уже .env файл
    if os.path.exists('.env'):
        overwrite = input("⚠️ Файл .env уже существует. Перезаписать? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Настройка отменена")
            return
    
    print("\n📋 Введите настройки для бота:")
    print("(Нажмите Enter для использования значений по умолчанию)")
    
    # API настройки
    print("\n🔑 Настройки Bybit API:")
    api_key = get_input("API Key Bybit")
    secret_key = get_input("Secret Key Bybit")
    testnet = get_input("Использовать тестовую сеть?", "true", required=False)
    
    # Торговые настройки
    print("\n💰 Настройки торговли:")
    symbol = get_input("Торговая пара", "BTCUSDT")
    quantity = get_input("Размер позиции", "0.001")
    
    # Настройки скальпинга
    print("\n📊 Настройки скальпинга:")
    profit_target = get_input("Take Profit (%)", "0.2")
    stop_loss = get_input("Stop Loss (%)", "0.1")
    max_positions = get_input("Максимум позиций", "3")
    
    # Технические индикаторы
    print("\n📈 Технические индикаторы:")
    rsi_period = get_input("Период RSI", "14")
    rsi_overbought = get_input("Уровень перекупленности RSI", "70")
    rsi_oversold = get_input("Уровень перепроданности RSI", "30")
    
    # Временные настройки
    print("\n⏰ Временные настройки:")
    candle_interval = get_input("Интервал свечей (минуты)", "1")
    position_timeout = get_input("Таймаут позиции (секунды)", "300")
    
    # Логирование
    print("\n📝 Настройки логирования:")
    log_level = get_input("Уровень логирования", "INFO")
    
    # Создаем содержимое .env файла
    env_content = f"""# Bybit API настройки
BYBIT_API_KEY={api_key}
BYBIT_SECRET_KEY={secret_key}
BYBIT_TESTNET={testnet}

# Настройки торговли
SYMBOL={symbol}
QUANTITY={quantity}

# Настройки скальпинга
PROFIT_TARGET={float(profit_target) / 100}
STOP_LOSS={float(stop_loss) / 100}
MAX_POSITIONS={max_positions}

# Технические индикаторы
RSI_PERIOD={rsi_period}
RSI_OVERBOUGHT={rsi_overbought}
RSI_OVERSOLD={rsi_oversold}

# Временные настройки
CANDLE_INTERVAL={candle_interval}
POSITION_TIMEOUT={position_timeout}

# Логирование
LOG_LEVEL={log_level}
"""
    
    # Записываем в файл
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ Файл .env успешно создан!")
        print(f"📁 Путь: {os.path.abspath('.env')}")
        
        # Показываем созданные настройки
        print("\n📋 Созданные настройки:")
        print(f"   Торговая пара: {symbol}")
        print(f"   Размер позиции: {quantity}")
        print(f"   Take Profit: {profit_target}%")
        print(f"   Stop Loss: {stop_loss}%")
        print(f"   Тестовая сеть: {testnet}")
        
        print("\n🚀 Теперь вы можете:")
        print("   1. Запустить тесты: python3 test_bot.py")
        print("   2. Запустить бота: python3 main.py")
        print("   3. Или использовать: ./run_bot.sh start")
        
    except Exception as e:
        print(f"❌ Ошибка при создании файла: {e}")
        return False
    
    return True

def main():
    """Главная функция"""
    try:
        success = create_env_file()
        if success:
            print("\n🎉 Настройка завершена успешно!")
        else:
            print("\n❌ Настройка не завершена")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Настройка отменена пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
