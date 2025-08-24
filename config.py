import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

class Config:
    # Bybit API настройки
    BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
    BYBIT_SECRET_KEY = os.getenv('BYBIT_SECRET_KEY')
    BYBIT_TESTNET = os.getenv('BYBIT_TESTNET', 'true').lower() == 'true'
    
    # Настройки торговли
    SYMBOL = os.getenv('SYMBOL', 'BTCUSDT')
    QUANTITY = float(os.getenv('QUANTITY', '0.001'))
    
    # Настройки скальпинга
    PROFIT_TARGET = float(os.getenv('PROFIT_TARGET', '0.002'))  # 0.2%
    STOP_LOSS = float(os.getenv('STOP_LOSS', '0.001'))  # 0.1%
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '3'))
    
    # Технические индикаторы
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', '14'))
    RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', '70'))
    RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', '30'))
    
    # Временные настройки
    CANDLE_INTERVAL = os.getenv('CANDLE_INTERVAL', '1')  # 1 минута
    POSITION_TIMEOUT = int(os.getenv('POSITION_TIMEOUT', '300'))  # 5 минут
    
    # Логирование
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls):
        """Проверяет корректность конфигурации"""
        if not cls.BYBIT_API_KEY or not cls.BYBIT_SECRET_KEY:
            raise ValueError("BYBIT_API_KEY и BYBIT_SECRET_KEY должны быть установлены")
        
        if cls.QUANTITY <= 0:
            raise ValueError("QUANTITY должен быть больше 0")
        
        if cls.PROFIT_TARGET <= 0 or cls.STOP_LOSS <= 0:
            raise ValueError("PROFIT_TARGET и STOP_LOSS должны быть больше 0")
        
        return True
