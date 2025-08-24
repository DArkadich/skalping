import asyncio
import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from bybit_client import BybitClient
from config import Config

class ScalpingStrategy:
    def __init__(self):
        self.config = Config()
        self.client = BybitClient()
        self.logger = logging.getLogger(__name__)
        
        # Состояние стратегии
        self.active_positions = []
        self.last_signal_time = None
        self.signal_cooldown = 60  # 60 секунд между сигналами
        
    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """Вычисляет RSI индикатор"""
        if len(prices) < period + 1:
            return 50.0
        
        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        
        avg_gains = np.mean(gains[:period])
        avg_losses = np.mean(losses[:period])
        
        if avg_losses == 0:
            return 100.0
        
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2) -> Tuple[float, float, float]:
        """Вычисляет полосы Боллинджера"""
        if len(prices) < period:
            return prices[-1], prices[-1], prices[-1]
        
        sma = np.mean(prices[-period:])
        std = np.std(prices[-period:])
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        return upper_band, sma, lower_band
    
    def calculate_macd(self, prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float, float]:
        """Вычисляет MACD индикатор"""
        if len(prices) < slow:
            return 0.0, 0.0, 0.0
        
        # Быстрая EMA
        ema_fast = self.calculate_ema(prices, fast)
        
        # Медленная EMA
        ema_slow = self.calculate_ema(prices, slow)
        
        # MACD линия
        macd_line = ema_fast - ema_slow
        
        # Сигнальная линия (EMA от MACD)
        macd_values = [macd_line]
        signal_line = self.calculate_ema(macd_values, signal)
        
        # Гистограмма
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def calculate_ema(self, prices: List[float], period: int) -> float:
        """Вычисляет экспоненциальную скользящую среднюю"""
        if len(prices) < period:
            return prices[-1]
        
        multiplier = 2 / (period + 1)
        ema = prices[0]
        
        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def analyze_market(self, kline_data: List[Dict]) -> Dict:
        """Анализирует рыночные данные и возвращает сигналы"""
        if not kline_data or len(kline_data) < 50:
            return {"signal": "HOLD", "strength": 0, "reason": "Недостаточно данных"}
        
        # Извлекаем цены закрытия
        close_prices = [float(candle['close']) for candle in kline_data]
        high_prices = [float(candle['high']) for candle in kline_data]
        low_prices = [float(candle['low']) for candle in kline_data]
        volumes = [float(candle['volume']) for candle in kline_data]
        
        # Вычисляем индикаторы
        rsi = self.calculate_rsi(close_prices, self.config.RSI_PERIOD)
        upper_bb, middle_bb, lower_bb = self.calculate_bollinger_bands(close_prices)
        macd_line, signal_line, histogram = self.calculate_macd(close_prices)
        
        # Текущая цена
        current_price = close_prices[-1]
        
        # Анализ сигналов
        signals = []
        signal_strength = 0
        
        # RSI сигналы
        if rsi < self.config.RSI_OVERSOLD:
            signals.append(f"RSI перепродан ({rsi:.2f})")
            signal_strength += 2
        elif rsi > self.config.RSI_OVERBOUGHT:
            signals.append(f"RSI перекуплен ({rsi:.2f})")
            signal_strength -= 2
        
        # Полосы Боллинджера
        if current_price < lower_bb:
            signals.append(f"Цена ниже нижней полосы Боллинджера")
            signal_strength += 1
        elif current_price > upper_bb:
            signals.append(f"Цена выше верхней полосы Боллинджера")
            signal_strength -= 1
        
        # MACD сигналы
        if macd_line > signal_line and histogram > 0:
            signals.append("MACD выше сигнальной линии")
            signal_strength += 1
        elif macd_line < signal_line and histogram < 0:
            signals.append("MACD ниже сигнальной линии")
            signal_strength -= 1
        
        # Анализ объема
        avg_volume = np.mean(volumes[-20:])
        current_volume = volumes[-1]
        if current_volume > avg_volume * 1.5:
            signals.append("Повышенный объем")
            signal_strength += 0.5
        
        # Определение сигнала
        if signal_strength >= 2:
            signal = "BUY"
        elif signal_strength <= -2:
            signal = "SELL"
        else:
            signal = "HOLD"
        
        return {
            "signal": signal,
            "strength": abs(signal_strength),
            "reason": "; ".join(signals) if signals else "Нет четких сигналов",
            "indicators": {
                "rsi": rsi,
                "bollinger_bands": {"upper": upper_bb, "middle": middle_bb, "lower": lower_bb},
                "macd": {"line": macd_line, "signal": signal_line, "histogram": histogram},
                "current_price": current_price
            }
        }
    
    async def should_open_position(self, symbol: str) -> Tuple[bool, str]:
        """Определяет, следует ли открывать позицию"""
        # Проверяем количество активных позиций
        if len(self.active_positions) >= self.config.MAX_POSITIONS:
            return False, "Достигнут лимит позиций"
        
        # Проверяем кулдаун между сигналами
        if (self.last_signal_time and 
            datetime.now() - self.last_signal_time < timedelta(seconds=self.signal_cooldown)):
            return False, "Кулдаун между сигналами"
        
        # Получаем данные свечей
        kline_data = await self.client.get_kline_data(
            symbol, 
            self.config.CANDLE_INTERVAL, 
            100
        )
        
        if not kline_data:
            return False, "Не удалось получить данные свечей"
        
        # Анализируем рынок
        analysis = self.analyze_market(kline_data)
        
        if analysis["signal"] in ["BUY", "SELL"] and analysis["strength"] >= 2:
            self.last_signal_time = datetime.now()
            return True, f"{analysis['signal']}: {analysis['reason']}"
        
        return False, f"Нет сигнала: {analysis['reason']}"
    
    async def should_close_position(self, position: Dict, current_price: float) -> Tuple[bool, str]:
        """Определяет, следует ли закрыть позицию"""
        entry_price = float(position['entry_price'])
        side = position['side']
        size = float(position['size'])
        
        if size == 0:
            return False, "Позиция уже закрыта"
        
        # Вычисляем P&L
        if side == "Buy":
            pnl_percent = (current_price - entry_price) / entry_price
        else:
            pnl_percent = (entry_price - current_price) / entry_price
        
        # Проверяем take profit
        if pnl_percent >= self.config.PROFIT_TARGET:
            return True, f"Take Profit достигнут: {pnl_percent:.4f}"
        
        # Проверяем stop loss
        if pnl_percent <= -self.config.STOP_LOSS:
            return True, f"Stop Loss достигнут: {pnl_percent:.4f}"
        
        # Проверяем timeout
        if 'open_time' in position:
            open_time = datetime.fromisoformat(position['open_time'].replace('Z', '+00:00'))
            if datetime.now() - open_time > timedelta(seconds=self.config.POSITION_TIMEOUT):
                return True, f"Timeout позиции: {self.config.POSITION_TIMEOUT} секунд"
        
        return False, f"P&L: {pnl_percent:.4f}"
    
    async def execute_trade(self, symbol: str, side: str, quantity: float) -> bool:
        """Выполняет торговую операцию"""
        try:
            # Размещаем ордер
            order = await self.client.place_order(
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type="Market"
            )
            
            if order and 'result' in order:
                # Добавляем позицию в активные
                position_info = {
                    'symbol': symbol,
                    'side': side,
                    'size': quantity,
                    'entry_price': await self.client.get_market_price(symbol),
                    'open_time': datetime.now().isoformat(),
                    'order_id': order['result']['order_id']
                }
                
                self.active_positions.append(position_info)
                self.logger.info(f"Позиция открыта: {position_info}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении торговой операции: {e}")
            return False
    
    async def close_position_by_id(self, position: Dict) -> bool:
        """Закрывает конкретную позицию"""
        try:
            success = await self.client.close_position(
                symbol=position['symbol'],
                side=position['side'],
                quantity=position['size']
            )
            
            if success:
                # Удаляем из активных позиций
                self.active_positions = [p for p in self.active_positions if p != position]
                self.logger.info(f"Позиция закрыта: {position}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Ошибка при закрытии позиции: {e}")
            return False
    
    async def update_positions(self, symbol: str):
        """Обновляет информацию о позициях"""
        try:
            current_positions = await self.client.get_open_positions(symbol)
            current_price = await self.client.get_market_price(symbol)
            
            if not current_price:
                return
            
            # Обновляем активные позиции
            for pos in self.active_positions[:]:
                should_close, reason = await self.should_close_position(pos, current_price)
                
                if should_close:
                    self.logger.info(f"Закрытие позиции: {reason}")
                    await self.close_position_by_id(pos)
                else:
                    self.logger.debug(f"Позиция активна: {reason}")
                    
        except Exception as e:
            self.logger.error(f"Ошибка при обновлении позиций: {e}")
    
    def get_strategy_status(self) -> Dict:
        """Возвращает текущий статус стратегии"""
        return {
            "active_positions": len(self.active_positions),
            "max_positions": self.config.MAX_POSITIONS,
            "last_signal_time": self.last_signal_time.isoformat() if self.last_signal_time else None,
            "positions": self.active_positions
        }
