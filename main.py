import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Dict, Optional

from config import Config
from bybit_client import BybitClient
from scalping_strategy import ScalpingStrategy

class ScalpingBot:
    def __init__(self):
        self.config = Config()
        self.client = BybitClient()
        self.strategy = ScalpingStrategy()
        self.running = False
        self.logger = self._setup_logging()
        
        # Обработчики сигналов для graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self) -> logging.Logger:
        """Настраивает логирование"""
        logging.basicConfig(
            level=getattr(logging, self.config.LOG_LEVEL),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scalping_bot.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        return logging.getLogger(__name__)
    
    def _signal_handler(self, signum, frame):
        """Обработчик сигналов для graceful shutdown"""
        self.logger.info(f"Получен сигнал {signum}, завершаем работу...")
        self.running = False
    
    async def initialize(self) -> bool:
        """Инициализирует бота"""
        try:
            self.logger.info("Инициализация бота скальпинга...")
            
            # Проверяем конфигурацию
            self.config.validate()
            self.logger.info("Конфигурация проверена")
            
            # Проверяем подключение к Bybit
            account_info = await self.client.get_account_info()
            if not account_info:
                self.logger.error("Не удалось подключиться к Bybit API")
                return False
            
            self.logger.info(f"Подключение к Bybit установлено: {account_info}")
            
            # Получаем текущую цену
            current_price = await self.client.get_market_price(self.config.SYMBOL)
            if current_price:
                self.logger.info(f"Текущая цена {self.config.SYMBOL}: {current_price}")
            
            # Отменяем все активные ордера
            await self.client.cancel_all_orders(self.config.SYMBOL)
            
            self.logger.info("Бот успешно инициализирован")
            return True
            
        except Exception as e:
            self.logger.error(f"Ошибка при инициализации: {e}")
            return False
    
    async def run_strategy_cycle(self):
        """Выполняет один цикл стратегии"""
        try:
            # Обновляем информацию о позициях
            await self.strategy.update_positions(self.config.SYMBOL)
            
            # Проверяем, следует ли открыть новую позицию
            should_open, reason = await self.strategy.should_open_position(self.config.SYMBOL)
            
            if should_open:
                # Определяем сторону торговли
                if "BUY" in reason:
                    side = "Buy"
                elif "SELL" in reason:
                    side = "Sell"
                else:
                    self.logger.warning(f"Неопределенная сторона торговли: {reason}")
                    return
                
                self.logger.info(f"Открываем позицию: {reason}")
                
                # Выполняем торговую операцию
                success = await self.strategy.execute_trade(
                    symbol=self.config.SYMBOL,
                    side=side,
                    quantity=self.config.QUANTITY
                )
                
                if success:
                    self.logger.info(f"Позиция {side} успешно открыта")
                else:
                    self.logger.error(f"Не удалось открыть позицию {side}")
            else:
                self.logger.debug(f"Нет сигнала для открытия позиции: {reason}")
                
        except Exception as e:
            self.logger.error(f"Ошибка в цикле стратегии: {e}")
    
    async def run(self):
        """Основной цикл работы бота"""
        try:
            # Инициализация
            if not await self.initialize():
                self.logger.error("Не удалось инициализировать бота")
                return
            
            self.running = True
            self.logger.info("Бот запущен и работает...")
            
            # Основной цикл
            while self.running:
                try:
                    # Выполняем цикл стратегии
                    await self.run_strategy_cycle()
                    
                    # Получаем статус стратегии
                    status = self.strategy.get_strategy_status()
                    self.logger.info(f"Статус: {status['active_positions']}/{status['max_positions']} позиций")
                    
                    # Ждем перед следующим циклом
                    await asyncio.sleep(10)  # 10 секунд между циклами
                    
                except asyncio.CancelledError:
                    self.logger.info("Получен сигнал отмены")
                    break
                except Exception as e:
                    self.logger.error(f"Ошибка в основном цикле: {e}")
                    await asyncio.sleep(30)  # Ждем 30 секунд при ошибке
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка: {e}")
        finally:
            await self.shutdown()
    
    async def shutdown(self):
        """Корректно завершает работу бота"""
        try:
            self.logger.info("Завершение работы бота...")
            
            # Закрываем все позиции
            for position in self.strategy.active_positions[:]:
                self.logger.info(f"Закрываем позицию: {position}")
                await self.strategy.close_position_by_id(position)
            
            # Отменяем все ордера
            await self.client.cancel_all_orders(self.config.SYMBOL)
            
            # Закрываем соединения
            self.client.close_connection()
            
            self.logger.info("Бот успешно завершил работу")
            
        except Exception as e:
            self.logger.error(f"Ошибка при завершении работы: {e}")
    
    async def get_bot_status(self) -> Dict:
        """Возвращает текущий статус бота"""
        try:
            account_info = await self.client.get_account_info()
            strategy_status = self.strategy.get_strategy_status()
            current_price = await self.client.get_market_price(self.config.SYMBOL)
            
            return {
                "running": self.running,
                "symbol": self.config.SYMBOL,
                "current_price": current_price,
                "account_info": account_info,
                "strategy_status": strategy_status,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Ошибка при получении статуса: {e}")
            return {"error": str(e)}

async def main():
    """Главная функция"""
    bot = ScalpingBot()
    
    try:
        await bot.run()
    except KeyboardInterrupt:
        print("\nПолучен сигнал прерывания, завершаем работу...")
    except Exception as e:
        print(f"Критическая ошибка: {e}")
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    # Запускаем бота
    asyncio.run(main())
