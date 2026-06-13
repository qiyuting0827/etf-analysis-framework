"""
Backtest execution engine - core backtesting logic
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Backtest configuration"""
    initial_capital: float = 100000
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005   # 0.05%
    position_size: float = 1.0  # 100% of capital per trade
    max_position: int = 1       # Max concurrent positions
    

class BacktestEngine:
    """
    Core backtesting engine
    Executes strategies on historical data and generates performance reports
    """
    
    def __init__(self, config: Optional[BacktestConfig] = None):
        """
        Initialize backtest engine
        
        Args:
            config: Backtest configuration
        """
        self.config = config or BacktestConfig()
        self.trades: List[Dict] = []
        self.equity_curve: List[float] = []
        self.cash: float = self.config.initial_capital
        self.position: float = 0
        self.entry_price: float = 0
    
    def run(
        self,
        data: pd.DataFrame,
        strategy,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> 'BacktestResult':
        """
        Run backtest on data with strategy
        
        Args:
            data: OHLCV data
            strategy: Strategy instance
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            BacktestResult object
        """
        # Filter data by dates
        if start_date:
            data = data[data.index >= start_date]
        if end_date:
            data = data[data.index <= end_date]
        
        if data.empty:
            raise ValueError("No data available for backtest period")
        
        logger.info(f"Starting backtest: {len(data)} bars")
        
        # Initialize
        strategy.data = data
        strategy.setup()
        
        self.trades = []
        self.equity_curve = []
        self.cash = self.config.initial_capital
        self.position = 0
        
        # Main backtest loop
        for i in range(len(data)):
            strategy.current_index = i
            
            # Get current bar
            current_bar = data.iloc[i]
            current_price = current_bar['close']
            
            # Update equity
            portfolio_value = self.cash + (self.position * current_price)
            self.equity_curve.append(portfolio_value)
            
            # Generate signal
            signal = strategy.next()
            
            # Execute signal
            if signal:
                self._execute_signal(signal, current_price, i, data.index[i])
        
        logger.info(f"Backtest completed. Total trades: {len(self.trades)}")
        
        # Generate results
        results = BacktestResult(
            data=data,
            trades=self.trades,
            equity_curve=self.equity_curve,
            initial_capital=self.config.initial_capital,
            final_capital=self.equity_curve[-1] if self.equity_curve else self.config.initial_capital,
        )
        
        return results
    
    def _execute_signal(self, signal, price: float, index: int, timestamp):
        """
        Execute trading signal
        
        Args:
            signal: Trading signal
            price: Current price
            index: Bar index
            timestamp: Bar timestamp
        """
        if signal.signal_type == 'buy':
            self._open_position(price, index, timestamp, signal)
        elif signal.signal_type == 'sell':
            self._close_position(price, index, timestamp, signal)
    
    def _open_position(self, price: float, index: int, timestamp, signal):
        """
        Open a long position
        
        Args:
            price: Entry price
            index: Bar index
            timestamp: Entry timestamp
            signal: Trading signal
        """
        if self.position > 0:
            return  # Already in position
        
        # Calculate position size
        position_size = (self.cash * self.config.position_size) / price
        commission = position_size * price * self.config.commission
        slippage_cost = position_size * price * self.config.slippage
        
        self.position = position_size
        self.entry_price = price
        self.cash -= position_size * price + commission + slippage_cost
        
        logger.debug(f"BUY: {position_size:.2f} @ {price:.2f}")
    
    def _close_position(self, price: float, index: int, timestamp, signal):
        """
        Close a long position
        
        Args:
            price: Exit price
            index: Bar index
            timestamp: Exit timestamp
            signal: Trading signal
        """
        if self.position <= 0:
            return  # No position to close
        
        # Calculate P&L
        pnl = self.position * (price - self.entry_price)
        commission = self.position * price * self.config.commission
        slippage_cost = self.position * price * self.config.slippage
        
        # Update cash
        self.cash += self.position * price - commission - slippage_cost
        
        # Record trade
        trade = {
            'entry_index': index - 1,
            'exit_index': index,
            'entry_price': float(self.entry_price),
            'exit_price': float(price),
            'quantity': float(self.position),
            'pnl': float(pnl),
            'commission': float(commission),
            'return': float(pnl / (self.position * self.entry_price)) if self.position > 0 else 0,
        }
        self.trades.append(trade)
        
        logger.debug(f"SELL: {self.position:.2f} @ {price:.2f}, P&L: {pnl:.2f}")
        
        self.position = 0
        self.entry_price = 0


@dataclass
class BacktestResult:
    """Backtest results"""
    data: pd.DataFrame
    trades: List[Dict]
    equity_curve: List[float]
    initial_capital: float
    final_capital: float
    
    @property
    def total_return(self) -> float:
        """Total return percentage"""
        if self.initial_capital == 0:
            return 0.0
        return (self.final_capital - self.initial_capital) / self.initial_capital
    
    @property
    def total_trades(self) -> int:
        """Total number of trades"""
        return len(self.trades)
    
    @property
    def winning_trades(self) -> int:
        """Number of winning trades"""
        return sum(1 for trade in self.trades if trade['pnl'] > 0)
    
    @property
    def losing_trades(self) -> int:
        """Number of losing trades"""
        return sum(1 for trade in self.trades if trade['pnl'] < 0)
    
    @property
    def win_rate(self) -> float:
        """Win rate"""
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
    
    @property
    def profit_factor(self) -> float:
        """Profit factor (gross profit / gross loss)"""
        gross_profit = sum(trade['pnl'] for trade in self.trades if trade['pnl'] > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in self.trades if trade['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return gross_profit / gross_loss
    
    @property
    def avg_trade_return(self) -> float:
        """Average return per trade"""
        if self.total_trades == 0:
            return 0.0
        total_pnl = sum(trade['pnl'] for trade in self.trades)
        return total_pnl / self.initial_capital / self.total_trades
    
    def __repr__(self) -> str:
        return (
            f"BacktestResult(Total Return: {self.total_return:.2%}, "
            f"Trades: {self.total_trades}, Win Rate: {self.win_rate:.2%})"
        )
