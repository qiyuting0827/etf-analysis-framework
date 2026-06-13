"""
Base class for trading strategies
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
import numpy as np
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Signal:
    """Trading signal"""
    timestamp: datetime
    signal_type: str  # 'buy', 'sell', 'hold'
    strength: float  # 0-1, signal strength
    reason: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class Strategy(ABC):
    """
    Base class for all trading strategies
    
    Provides a unified interface for strategy implementation
    """
    
    def __init__(self, name: str, **params):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
            **params: Strategy parameters
        """
        self.name = name
        self.params = params
        self.indicators: Dict[str, Any] = {}
        self.signals: List[Signal] = []
        self.data: Optional[pd.DataFrame] = None
        self.current_index: int = 0
        self.position: float = 0  # Current position size
        self.entry_price: float = 0
        self.entry_time: Optional[datetime] = None
    
    @abstractmethod
    def setup(self):
        """
        Setup indicators and initialize strategy
        Called once before backtesting
        """
        pass
    
    @abstractmethod
    def next(self) -> Optional[Signal]:
        """
        Generate trading signals for current bar
        Called for each bar during backtesting
        
        Returns:
            Trading signal or None
        """
        pass
    
    def on_bar(self, bar_data: Dict[str, float], index: int):
        """
        Called when a new bar arrives
        
        Args:
            bar_data: Current bar data (open, high, low, close, volume)
            index: Bar index
        """
        self.current_index = index
    
    def add_indicator(self, name: str, indicator: Any) -> Any:
        """
        Add indicator to strategy
        
        Args:
            name: Indicator name
            indicator: Indicator instance
            
        Returns:
            Indicator instance
        """
        self.indicators[name] = indicator
        return indicator
    
    def generate_signal(
        self,
        signal_type: str,
        strength: float = 1.0,
        reason: str = "",
        metadata: Optional[Dict] = None,
    ) -> Signal:
        """
        Generate a trading signal
        
        Args:
            signal_type: 'buy' or 'sell'
            strength: Signal strength (0-1)
            reason: Reason for signal
            metadata: Additional metadata
            
        Returns:
            Signal object
        """
        if metadata is None:
            metadata = {}
        
        timestamp = self.data.index[self.current_index] if self.data is not None else datetime.now()
        
        signal = Signal(
            timestamp=timestamp,
            signal_type=signal_type,
            strength=min(1.0, max(0.0, strength)),
            reason=reason,
            metadata=metadata
        )
        
        self.signals.append(signal)
        return signal
    
    def get_current_price(self) -> float:
        """
        Get current close price
        
        Returns:
            Current price
        """
        if self.data is None or self.current_index >= len(self.data):
            return 0.0
        return self.data['close'].iloc[self.current_index]
    
    def get_bar_data(self, offset: int = 0) -> Dict[str, float]:
        """
        Get bar data at specified offset
        
        Args:
            offset: Offset from current bar (0 = current, -1 = previous)
            
        Returns:
            Bar data dictionary
        """
        if self.data is None:
            return {}
        
        idx = self.current_index + offset
        if idx < 0 or idx >= len(self.data):
            return {}
        
        row = self.data.iloc[idx]
        return {
            'open': row['open'],
            'high': row['high'],
            'low': row['low'],
            'close': row['close'],
            'volume': row['volume'],
            'time': row.name,
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
