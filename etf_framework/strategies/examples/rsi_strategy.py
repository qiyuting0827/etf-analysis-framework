"""
RSI Strategy
"""

import numpy as np
from etf_framework.strategies.base import Strategy, Signal
from etf_framework.indicators.momentum import RSI
import logging

logger = logging.getLogger(__name__)


class RSIStrategy(Strategy):
    """
    RSI (Relative Strength Index) Strategy
    Buy when RSI < oversold threshold, Sell when RSI > overbought threshold
    """
    
    def __init__(
        self,
        period: int = 14,
        overbought: float = 70,
        oversold: float = 30,
        **kwargs
    ):
        """
        Initialize RSI Strategy
        
        Args:
            period: RSI period
            overbought: Overbought threshold
            oversold: Oversold threshold
            **kwargs: Additional parameters
        """
        super().__init__(name='RSI_Strategy', **kwargs)
        self.period = period
        self.overbought = overbought
        self.oversold = oversold
        self.rsi = None
    
    def setup(self):
        """
        Setup RSI indicator
        """
        self.rsi = self.add_indicator('RSI', RSI(period=self.period))
    
    def next(self) -> Signal:
        """
        Generate signals based on RSI levels
        
        Returns:
            Trading signal
        """
        if self.data is None or self.current_index < self.period:
            return None
        
        # Calculate RSI
        close_prices = self.data['close'].values[:self.current_index + 1]
        self.rsi.calculate(close_prices)
        
        if not self.rsi.is_ready:
            return None
        
        current_rsi = self.rsi.current_value
        
        # Check RSI levels
        if current_rsi < self.oversold:
            # Oversold - potential BUY
            strength = (self.oversold - current_rsi) / self.oversold
            return self.generate_signal(
                signal_type='buy',
                strength=strength,
                reason=f'RSI Oversold: {current_rsi:.2f} < {self.oversold}',
                metadata={'rsi': float(current_rsi)}
            )
        
        elif current_rsi > self.overbought:
            # Overbought - potential SELL
            strength = (current_rsi - self.overbought) / (100 - self.overbought)
            return self.generate_signal(
                signal_type='sell',
                strength=strength,
                reason=f'RSI Overbought: {current_rsi:.2f} > {self.overbought}',
                metadata={'rsi': float(current_rsi)}
            )
        
        return None
