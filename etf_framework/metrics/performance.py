"""
Performance metrics calculation
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """
    Calculate performance metrics from returns or equity curves
    """
    
    @staticmethod
    def calculate_returns(
        prices: np.ndarray,
        compound: bool = True,
    ) -> np.ndarray:
        """
        Calculate returns from price series
        
        Args:
            prices: Price series
            compound: Use compound returns
            
        Returns:
            Returns array
        """
        if compound:
            return np.diff(prices) / prices[:-1]
        else:
            return np.diff(prices)
    
    @staticmethod
    def calculate_cumulative_returns(
        returns: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate cumulative returns
        
        Args:
            returns: Returns array
            
        Returns:
            Cumulative returns
        """
        return np.cumprod(1 + returns) - 1
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: np.ndarray,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> float:
        """
        Calculate Sharpe ratio
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year
            
        Returns:
            Sharpe ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_sortino_ratio(
        returns: np.ndarray,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> float:
        """
        Calculate Sortino ratio
        
        Args:
            returns: Daily returns
            risk_free_rate: Annual risk-free rate
            periods_per_year: Trading periods per year
            
        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0
        
        excess_returns = returns - (risk_free_rate / periods_per_year)
        downside_returns = np.minimum(excess_returns, 0)
        downside_std = np.std(downside_returns)
        
        if downside_std == 0:
            return 0.0
        
        return np.mean(excess_returns) / downside_std * np.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_max_drawdown(
        prices: np.ndarray,
    ) -> Tuple[float, int, int]:
        """
        Calculate maximum drawdown
        
        Args:
            prices: Price series
            
        Returns:
            Tuple of (max_drawdown, start_idx, end_idx)
        """
        cumulative = np.cumprod(1 + np.diff(prices) / prices[:-1])
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        
        max_dd_idx = np.argmin(drawdown)
        max_dd = drawdown[max_dd_idx]
        
        # Find start of drawdown
        start_idx = np.where(running_max[:max_dd_idx] == running_max[max_dd_idx])[0]
        start_idx = start_idx[-1] if len(start_idx) > 0 else 0
        
        return float(max_dd), int(start_idx), int(max_dd_idx)
    
    @staticmethod
    def calculate_calmar_ratio(
        returns: np.ndarray,
        prices: np.ndarray,
        periods_per_year: int = 252,
    ) -> float:
        """
        Calculate Calmar ratio (Annual Return / Max Drawdown)
        
        Args:
            returns: Daily returns
            prices: Price series
            periods_per_year: Trading periods per year
            
        Returns:
            Calmar ratio
        """
        annual_return = np.mean(returns) * periods_per_year
        max_dd, _, _ = PerformanceMetrics.calculate_max_drawdown(prices)
        
        if max_dd == 0:
            return 0.0
        
        return annual_return / abs(max_dd)
    
    @staticmethod
    def calculate_win_rate(
        trades: List[Dict],
    ) -> float:
        """
        Calculate win rate
        
        Args:
            trades: List of trades
            
        Returns:
            Win rate (0-1)
        """
        if len(trades) == 0:
            return 0.0
        
        winning = sum(1 for trade in trades if trade['pnl'] > 0)
        return winning / len(trades)
    
    @staticmethod
    def calculate_profit_factor(
        trades: List[Dict],
    ) -> float:
        """
        Calculate profit factor
        
        Args:
            trades: List of trades
            
        Returns:
            Profit factor
        """
        gross_profit = sum(trade['pnl'] for trade in trades if trade['pnl'] > 0)
        gross_loss = abs(sum(trade['pnl'] for trade in trades if trade['pnl'] < 0))
        
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        
        return gross_profit / gross_loss
