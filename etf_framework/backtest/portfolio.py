"""
Portfolio management during backtest
"""

from typing import Dict, List, Optional
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents a position in a security"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: int
    
    @property
    def value(self) -> float:
        """Position value (without current price)"""
        return self.quantity * self.entry_price


class Portfolio:
    """
    Portfolio management
    """
    
    def __init__(
        self,
        initial_cash: float = 100000,
        commission: float = 0.001,
        slippage: float = 0.0005,
    ):
        """
        Initialize portfolio
        
        Args:
            initial_cash: Initial cash
            commission: Commission rate
            slippage: Slippage rate
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.commission = commission
        self.slippage = slippage
        self.positions: Dict[str, Position] = {}
        self.trade_history: List[Dict] = []
    
    def buy(
        self,
        symbol: str,
        quantity: float,
        price: float,
        timestamp: int,
    ) -> bool:
        """
        Buy a security
        
        Args:
            symbol: Security symbol
            quantity: Quantity to buy
            price: Buy price
            timestamp: Timestamp
            
        Returns:
            True if successful
        """
        total_cost = quantity * price
        commission = total_cost * self.commission
        slippage = total_cost * self.slippage
        total_required = total_cost + commission + slippage
        
        if total_required > self.cash:
            logger.warning(f"Insufficient cash to buy {quantity} {symbol}")
            return False
        
        self.cash -= total_required
        self.positions[symbol] = Position(
            symbol=symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=timestamp,
        )
        
        self.trade_history.append({
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'commission': commission,
            'slippage': slippage,
            'timestamp': timestamp,
        })
        
        logger.debug(f"BUY: {quantity} {symbol} @ {price}")
        return True
    
    def sell(
        self,
        symbol: str,
        quantity: Optional[float] = None,
        price: float = 0.0,
        timestamp: int = 0,
    ) -> bool:
        """
        Sell a security
        
        Args:
            symbol: Security symbol
            quantity: Quantity to sell (None = all)
            price: Sell price
            timestamp: Timestamp
            
        Returns:
            True if successful
        """
        if symbol not in self.positions:
            logger.warning(f"No position to sell: {symbol}")
            return False
        
        position = self.positions[symbol]
        quantity = quantity or position.quantity
        
        if quantity > position.quantity:
            logger.warning(f"Insufficient quantity to sell {symbol}")
            return False
        
        proceeds = quantity * price
        commission = proceeds * self.commission
        slippage = proceeds * self.slippage
        net_proceeds = proceeds - commission - slippage
        
        self.cash += net_proceeds
        
        if quantity == position.quantity:
            del self.positions[symbol]
        else:
            position.quantity -= quantity
        
        pnl = quantity * (price - position.entry_price)
        
        self.trade_history.append({
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'entry_price': position.entry_price,
            'pnl': pnl,
            'commission': commission,
            'slippage': slippage,
            'timestamp': timestamp,
        })
        
        logger.debug(f"SELL: {quantity} {symbol} @ {price}, P&L: {pnl}")
        return True
    
    def get_portfolio_value(self, prices: Dict[str, float]) -> float:
        """
        Get total portfolio value
        
        Args:
            prices: Current prices for positions
            
        Returns:
            Total portfolio value
        """
        position_value = sum(
            position.quantity * prices.get(symbol, position.entry_price)
            for symbol, position in self.positions.items()
        )
        return self.cash + position_value
    
    def get_holdings(self) -> Dict[str, float]:
        """
        Get current holdings
        
        Returns:
            Dictionary of symbol -> quantity
        """
        return {symbol: position.quantity for symbol, position in self.positions.items()}
    
    def reset(self):
        """
        Reset portfolio to initial state
        """
        self.cash = self.initial_cash
        self.positions.clear()
        self.trade_history.clear()
