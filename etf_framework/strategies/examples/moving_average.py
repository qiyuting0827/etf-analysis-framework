"""
Moving Average Crossover Strategy
"""

import numpy as np
from etf_framework.strategies.base import Strategy, Signal
from etf_framework.indicators.trend import SMA, EMA
import logging

logger = logging.getLogger(__name__)


class MovingAverageCrossover(Strategy):
    """
    Classic Moving Average Crossover Strategy
    Buy when short MA > long MA, Sell when short MA < long MA
    """
    
    def __init__(
        self,
        short_period: int = 20,
        long_period: int = 50,
        use_ema: bool = False,
        **kwargs
    ):
        """
        Initialize MA Crossover Strategy
        
        Args:
            short_period: Short MA period
            long_period: Long MA period
            use_ema: Use EMA instead of SMA
            **kwargs: Additional parameters
        """
        super().__init__(name='MA_Crossover', **kwargs)
        self.short_period = short_period
        self.long_period = long_period
        self.use_ema = use_ema
        self.ma_short = None
        self.ma_long = None
        self.last_crossover = None
    
    def setup(self):
        """
        Setup moving averages
        """
        ma_class = EMA if self.use_ema else SMA
        self.ma_short = self.add_indicator(
            f'MA_short_{self.short_period}',
            ma_class(period=self.short_period)
        )
        self.ma_long = self.add_indicator(
            f'MA_long_{self.long_period}',
            ma_class(period=self.long_period)
        )
    
    def next(self) -> Signal:
        """
        Generate signals based on MA crossover
        
        Returns:
            Trading signal
        """
        if not self.data is not None or self.current_index < self.long_period:
            return None
        
        # Calculate MAs if not already calculated
        close_prices = self.data['close'].values[:self.current_index + 1]
        
        self.ma_short.calculate(close_prices)
        self.ma_long.calculate(close_prices)
        
        if self.current_index < 1:
            return None
        
        current_short = self.ma_short.values[-1]
        current_long = self.ma_long.values[-1]
        
        if np.isnan(current_short) or np.isnan(current_long):
            return None
        
        previous_short = self.ma_short.values[-2]
        previous_long = self.ma_long.values[-2]
        
        # Check for crossover
        if previous_short <= previous_long and current_short > current_long:
            # Golden cross - BUY
            return self.generate_signal(
                signal_type='buy',
                strength=0.8,
                reason=f'Golden Cross: SMA{self.short_period} > SMA{self.long_period}',
                metadata={
                    'short_ma': float(current_short),
                    'long_ma': float(current_long),
                }
            )
        
        elif previous_short >= previous_long and current_short < current_long:
            # Death cross - SELL
            return self.generate_signal(
                signal_type='sell',
                strength=0.8,
                reason=f'Death Cross: SMA{self.short_period} < SMA{self.long_period}',
                metadata={
                    'short_ma': float(current_short),
                    'long_ma': float(current_long),
                }
            )
        
        return None
