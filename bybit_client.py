import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pybit.unified_trading import HTTP
from pybit.unified_trading import WebSocket
from config import Config

class BybitClient:
    def __init__(self):
        self.config = Config()
        self.session = HTTP(
            testnet=self.config.BYBIT_TESTNET,
            api_key=self.config.BYBIT_API_KEY,
            api_secret=self.config.BYBIT_SECRET_KEY
        )
        
        self.ws = WebSocket(
            testnet=self.config.BYBIT_TESTNET,
            channel_type="linear"
        )
        
        self.logger = logging.getLogger(__name__)
        
    async def get_account_info(self) -> Dict:
        """Получает информацию об аккаунте"""
        try:
            response = self.session.get_wallet_balance(accountType="UNIFIED", coin="USDT")
            return response
        except Exception as e:
            self.logger.error(f"Ошибка при получении информации об аккаунте: {e}")
            return {}
    
    async def get_market_price(self, symbol: str) -> Optional[float]:
        """Получает текущую рыночную цену"""
        try:
            response = self.session.get_tickers(category="linear", symbol=symbol)
            if response and 'result' in response and response['result'] and 'list' in response['result']:
                return float(response['result']['list'][0]['lastPrice'])
            return None
        except Exception as e:
            self.logger.error(f"Ошибка при получении рыночной цены: {e}")
            return None
    
    async def get_kline_data(self, symbol: str, interval: str, limit: int = 100) -> List[Dict]:
        """Получает данные свечей"""
        try:
            response = self.session.get_kline(
                category="linear",
                symbol=symbol,
                interval=interval,
                limit=limit
            )
            if response and 'result' in response and 'list' in response['result']:
                return response['result']['list']
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении данных свечей: {e}")
            return []
    
    async def place_order(self, symbol: str, side: str, quantity: float, 
                         order_type: str = "Market", price: Optional[float] = None) -> Dict:
        """Размещает ордер"""
        try:
            order_params = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": str(quantity),
                "timeInForce": "GTC"
            }
            
            if price and order_type == "Limit":
                order_params["price"] = str(price)
            
            response = self.session.place_order(**order_params)
            self.logger.info(f"Ордер размещен: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Ошибка при размещении ордера: {e}")
            return {}
    
    async def close_position(self, symbol: str, side: str, quantity: float) -> Dict:
        """Закрывает позицию"""
        try:
            # Для закрытия позиции используем противоположную сторону
            close_side = "Sell" if side == "Buy" else "Buy"
            response = await self.place_order(symbol, close_side, quantity)
            self.logger.info(f"Позиция закрыта: {response}")
            return response
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии позиции: {e}")
            return {}
    
    async def get_open_positions(self, symbol: str) -> List[Dict]:
        """Получает открытые позиции"""
        try:
            response = self.session.get_positions(category="linear", symbol=symbol)
            if response and 'result' in response and 'list' in response['result']:
                positions = []
                for pos in response['result']['list']:
                    if float(pos['size']) > 0:
                        positions.append(pos)
                return positions
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении открытых позиций: {e}")
            return []
    
    async def cancel_all_orders(self, symbol: str) -> bool:
        """Отменяет все ордера для символа"""
        try:
            response = self.session.cancel_all_orders(category="linear", symbol=symbol)
            self.logger.info(f"Все ордера отменены: {response}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отмене ордеров: {e}")
            return False
    
    async def get_order_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Получает историю ордеров"""
        try:
            response = self.session.get_open_orders(
                category="linear",
                symbol=symbol,
                limit=limit
            )
            if response and 'result' in response and 'list' in response['result']:
                return response['result']['list']
            return []
        except Exception as e:
            self.logger.error(f"Ошибка при получении истории ордеров: {e}")
            return []
    
    def subscribe_to_ticker(self, symbol: str, callback):
        """Подписывается на обновления тикера"""
        try:
            self.ws.ticker_stream(
                symbol=symbol,
                callback=callback
            )
        except Exception as e:
            self.logger.error(f"Ошибка при подписке на тикер: {e}")
    
    def close_connection(self):
        """Закрывает WebSocket соединение"""
        try:
            self.ws.close()
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии соединения: {e}")
