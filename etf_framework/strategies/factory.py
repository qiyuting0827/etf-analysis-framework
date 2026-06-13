"""
Strategy Factory for creating strategy instances
"""

from typing import Type, Dict, Any, Optional
from etf_framework.strategies.base import Strategy
from etf_framework.strategies.examples.moving_average import MovingAverageCrossover
from etf_framework.strategies.examples.rsi_strategy import RSIStrategy
from etf_framework.strategies.examples.macd_strategy import MACDStrategy
import logging

logger = logging.getLogger(__name__)


class StrategyFactory:
    """
    Factory for creating strategy instances
    """
    
    _strategies: Dict[str, Type[Strategy]] = {
        'MovingAverageCrossover': MovingAverageCrossover,
        'RSI': RSIStrategy,
        'MACD': MACDStrategy,
    }
    
    @classmethod
    def create(
        cls,
        strategy_name: str,
        **params
    ) -> Strategy:
        """
        Create a strategy instance
        
        Args:
            strategy_name: Name of strategy
            **params: Strategy parameters
            
        Returns:
            Strategy instance
            
        Raises:
            ValueError: If strategy not found
        """
        if strategy_name not in cls._strategies:
            raise ValueError(
                f"Strategy '{strategy_name}' not found. "
                f"Available: {', '.join(cls._strategies.keys())}"
            )
        
        strategy_class = cls._strategies[strategy_name]
        try:
            strategy = strategy_class(**params)
            logger.info(f"Created strategy: {strategy_name}")
            return strategy
        except Exception as e:
            logger.error(f"Error creating strategy {strategy_name}: {str(e)}")
            raise
    
    @classmethod
    def register(
        cls,
        name: str,
        strategy_class: Type[Strategy]
    ):
        """
        Register a custom strategy
        
        Args:
            name: Strategy name
            strategy_class: Strategy class
        """
        cls._strategies[name] = strategy_class
        logger.info(f"Registered strategy: {name}")
    
    @classmethod
    def list_strategies(cls) -> Dict[str, Type[Strategy]]:
        """
        List all available strategies
        
        Returns:
            Dictionary of strategy names and classes
        """
        return cls._strategies.copy()
