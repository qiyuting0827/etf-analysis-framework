"""
MACD Strategy
"""

import numpy as np
from etf_framework.strategies.base import Strategy, Signal
from etf_framework.indicators.momentum import MACD
from etf_framework.indicators.trend import EMA
import logging

logger = logging.getLogger(__name__)


class MACDStrategy(Strategy):
    """
    MACD (Moving Average Convergence Divergence) Strategy
    Buy when MACD > Signal Line, Sell when MACD < Signal Line
    """
    
    def __init__(
        self,
        fast: int = 12,
        slow: int = 26,
        signal_period: int = 9,
        **kwargs
    ):
        """
        Initialize MACD Strategy
        
        Args:
            fast: Fast EMA period
            slow: Slow EMA period
            signal_period: Signal line period
            **kwargs: Additional parameters
        """
        super().__init__(name='MACD_Strategy', **kwargs)
        self.fast = fast
        self.slow = slow
        self.signal_period = signal_period
        self.macd = None
        self.signal_line = None
    
    def setup(self):
        """
        Setup MACD indicator
        """
        self.macd = self.add_indicator(
            'MACD',
            MACD(fast=self.fast, slow=self.slow, signal=self.signal_period)
        )
    
    def next(self) -> Signal:
        """
        Generate signals based on MACD crossover
        
        Returns:
            Trading signal
        """
        if self.data is None or self.current_index < self.slow + self.signal_period:
            return None
        
        # Calculate MACD
        close_prices = self.data['close'].values[:self.current_index + 1]
        macd_values = self.macd.calculate(close_prices)
        
        # Calculate Signal Line (9-day EMA of MACD)
        signal_line = self._calculate_signal_line(macd_values)
        
        if self.current_index < 1:
            return None
        
        current_macd = macd_values[-1]
        current_signal = signal_line[-1]
        
        if np.isnan(current_macd) or np.isnan(current_signal):
            return None
        
        previous_macd = macd_values[-2]
        previous_signal = signal_line[-2]
        
        # Check for crossover
        if previous_macd <= previous_signal and current_macd > current_signal:
            # MACD > Signal - BUY
            return self.generate_signal(
                signal_type='buy',
                strength=0.7,
                reason=f'MACD crosses above Signal Line',
                metadata={
                    'macd': float(current_macd),
                    'signal': float(current_signal),
                    'histogram': float(current_macd - current_signal),
                }
            )
        
        elif previous_macd >= previous_signal and current_macd < current_signal:
            # MACD < Signal - SELL
            return self.generate_signal(
                signal_type='sell',
                strength=0.7,
                reason=f'MACD crosses below Signal Line',
                metadata={
                    'macd': float(current_macd),
                    'signal': float(current_signal),
                    'histogram': float(current_macd - current_signal),
                }
            )
        
        return None
    
    def _calculate_signal_line(self, macd_values: np.ndarray) -> np.ndarray:
        """
        Calculate signal line (EMA of MACD)
        
        Args:
            macd_values: MACD values
            
        Returns:
            Signal line values
        """
        # Remove NaN values for EMA calculation
        valid_macd = macd_values[~np.isnan(macd_values)]
        
        signal = np.full_like(macd_values, np.nan, dtype=float)
        alpha = 2 / (self.signal_period + 1)
        
        if len(valid_macd) >= self.signal_period:
            signal[len(macd_values) - len(valid_macd) + self.signal_period - 1] = np.mean(
                valid_macd[:self.signal_period]
            )
            
            for i in range(
                len(macd_values) - len(valid_macd) + self.signal_period,
                len(macd_values)
            ):
                if not np.isnan(signal[i - 1]) and not np.isnan(macd_values[i]):
                    signal[i] = alpha * macd_values[i] + (1 - alpha) * signal[i - 1]
        
        return signal
