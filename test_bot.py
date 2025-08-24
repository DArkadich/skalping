#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы бота скальпинга
Запускает бота в тестовом режиме без реальной торговли
"""

import asyncio
import logging
from config import Config
from bybit_client import BybitClient
from scalping_strategy import ScalpingStrategy

async def test_connection():
    """Тестирует подключение к Bybit API"""
    print("🔌 Тестирование подключения к Bybit API...")
    
    try:
        client = BybitClient()
        
        # Тест получения информации об аккаунте
        account_info = await client.get_account_info()
        if account_info:
            print("✅ Подключение к API успешно установлено")
            print(f"📊 Информация об аккаунте: {account_info}")
        else:
            print("❌ Не удалось получить информацию об аккаунте")
            return False
        
        # Тест получения текущей цены
        current_price = await client.get_market_price(Config.SYMBOL)
        if current_price:
            print(f"💰 Текущая цена {Config.SYMBOL}: {current_price}")
        else:
            print(f"❌ Не удалось получить цену для {Config.SYMBOL}")
            return False
        
        # Тест получения данных свечей
        kline_data = await client.get_kline_data(Config.SYMBOL, Config.CANDLE_INTERVAL, 10)
        if kline_data:
            print(f"📈 Получено {len(kline_data)} свечей")
        else:
            print("❌ Не удалось получить данные свечей")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании подключения: {e}")
        return False

async def test_strategy():
    """Тестирует стратегию скальпинга"""
    print("\n📊 Тестирование стратегии скальпинга...")
    
    try:
        strategy = ScalpingStrategy()
        
        # Получаем данные для анализа
        client = BybitClient()
        kline_data = await client.get_kline_data(Config.SYMBOL, Config.CANDLE_INTERVAL, 100)
        
        if not kline_data:
            print("❌ Не удалось получить данные для анализа")
            return False
        
        # Анализируем рынок
        analysis = strategy.analyze_market(kline_data)
        
        print(f"📊 Результат анализа:")
        print(f"   Сигнал: {analysis['signal']}")
        print(f"   Сила сигнала: {analysis['strength']}")
        print(f"   Причина: {analysis['reason']}")
        
        if 'indicators' in analysis:
            indicators = analysis['indicators']
            print(f"   RSI: {indicators.get('rsi', 'N/A'):.2f}")
            print(f"   Текущая цена: {indicators.get('current_price', 'N/A'):.2f}")
        
        # Тест проверки открытия позиции
        should_open, reason = await strategy.should_open_position(Config.SYMBOL)
        print(f"\n🔍 Проверка открытия позиции:")
        print(f"   Следует открыть: {should_open}")
        print(f"   Причина: {reason}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании стратегии: {e}")
        return False

async def test_configuration():
    """Тестирует конфигурацию"""
    print("\n⚙️ Тестирование конфигурации...")
    
    try:
        config = Config()
        
        print(f"📋 Параметры конфигурации:")
        print(f"   Символ: {config.SYMBOL}")
        print(f"   Размер позиции: {config.QUANTITY}")
        print(f"   Take Profit: {config.PROFIT_TARGET:.4f}")
        print(f"   Stop Loss: {config.STOP_LOSS:.4f}")
        print(f"   Макс. позиций: {config.MAX_POSITIONS}")
        print(f"   Тестовая сеть: {config.BYBIT_TESTNET}")
        print(f"   RSI период: {config.RSI_PERIOD}")
        print(f"   Интервал свечей: {config.CANDLE_INTERVAL} мин")
        
        # Валидация конфигурации
        try:
            config.validate()
            print("✅ Конфигурация валидна")
            return True
        except ValueError as e:
            print(f"❌ Ошибка валидации: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при тестировании конфигурации: {e}")
        return False

async def main():
    """Главная функция тестирования"""
    print("🧪 Запуск тестирования бота скальпинга...\n")
    
    # Тест конфигурации
    config_ok = await test_configuration()
    if not config_ok:
        print("\n❌ Тест конфигурации не пройден")
        return
    
    # Тест подключения
    connection_ok = await test_connection()
    if not connection_ok:
        print("\n❌ Тест подключения не пройден")
        return
    
    # Тест стратегии
    strategy_ok = await test_strategy()
    if not strategy_ok:
        print("\n❌ Тест стратегии не пройден")
        return
    
    print("\n🎉 Все тесты пройдены успешно!")
    print("🚀 Бот готов к работе")
    
    # Выводим рекомендации
    print("\n📝 Рекомендации:")
    print("   1. Убедитесь, что API ключи корректны")
    print("   2. Начните с тестовой сети (BYBIT_TESTNET=true)")
    print("   3. Используйте малые размеры позиций для начала")
    print("   4. Регулярно мониторьте работу бота")

if __name__ == "__main__":
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Запускаем тесты
    asyncio.run(main())
