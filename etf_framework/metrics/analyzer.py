"""
Metrics analyzer - comprehensive analysis
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from dataclasses import dataclass
from etf_framework.metrics.performance import PerformanceMetrics
from etf_framework.metrics.risk import RiskMetrics
import logging

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Comprehensive analysis result"""
    # Returns
    total_return: float
    annual_return: float
    monthly_returns: np.ndarray
    
    # Risk
    volatility: float
    max_drawdown: float
    
    # Risk-adjusted Returns
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    
    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    avg_trade_return: float
    
    # Additional
    best_day: float
    worst_day: float
    
    def summary(self) -> str:
        """Get summary string"""
        return f"""
Performance Analysis Summary
{'='*50}
Total Return:        {self.total_return:.2%}
Annual Return:       {self.annual_return:.2%}
Volatility:          {self.volatility:.2%}
Max Drawdown:        {self.max_drawdown:.2%}

Risk-Adjusted Metrics
Sharpe Ratio:        {self.sharpe_ratio:.2f}
Sortino Ratio:       {self.sortino_ratio:.2f}
Calmar Ratio:        {self.calmar_ratio:.2f}

Trade Statistics
Total Trades:        {self.total_trades}
Winning Trades:      {self.winning_trades}
Losing Trades:       {self.losing_trades}
Win Rate:            {self.win_rate:.2%}
Profit Factor:       {self.profit_factor:.2f}
Avg Trade Return:    {self.avg_trade_return:.2%}

Daily Returns
Best Day:            {self.best_day:.2%}
Worst Day:           {self.worst_day:.2%}
"""


class MetricsAnalyzer:
    """
    Comprehensive metrics analyzer
    """
    
    @staticmethod
    def analyze(
        data: pd.DataFrame,
        trades: List[Dict],
        equity_curve: List[float],
        initial_capital: float,
        risk_free_rate: float = 0.02,
        periods_per_year: int = 252,
    ) -> AnalysisResult:
        """
        Perform comprehensive analysis
        
        Args:
            data: Price data
            trades: List of trades
            equity_curve: Equity curve
            initial_capital: Initial capital
            risk_free_rate: Risk-free rate
            periods_per_year: Periods per year
            
        Returns:
            AnalysisResult object
        """
        equity_array = np.array(equity_curve)
        prices = data['close'].values
        
        # Calculate returns
        returns = PerformanceMetrics.calculate_returns(equity_array)
        
        # Performance metrics
        total_return = (equity_array[-1] - initial_capital) / initial_capital
        annual_return = (1 + total_return) ** (periods_per_year / len(equity_array)) - 1
        
        # Risk metrics
        volatility = RiskMetrics.calculate_volatility(returns, periods_per_year)
        max_dd, _, _ = PerformanceMetrics.calculate_max_drawdown(equity_array)
        
        # Risk-adjusted returns
        sharpe_ratio = PerformanceMetrics.calculate_sharpe_ratio(
            returns, risk_free_rate, periods_per_year
        )
        sortino_ratio = PerformanceMetrics.calculate_sortino_ratio(
            returns, risk_free_rate, periods_per_year
        )
        calmar_ratio = PerformanceMetrics.calculate_calmar_ratio(
            returns, equity_array, periods_per_year
        )
        
        # Trade statistics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade['pnl'] > 0)
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        profit_factor = PerformanceMetrics.calculate_profit_factor(trades)
        avg_trade_return = sum(trade['pnl'] for trade in trades) / initial_capital / total_trades if total_trades > 0 else 0
        
        # Daily returns statistics
        daily_returns = np.diff(prices) / prices[:-1]
        best_day = np.max(daily_returns) if len(daily_returns) > 0 else 0
        worst_day = np.min(daily_returns) if len(daily_returns) > 0 else 0
        
        # Monthly returns
        monthly_data = pd.Series(equity_array, index=data.index)
        monthly_returns = monthly_data.resample('M').last().pct_change().values[1:]
        
        return AnalysisResult(
            total_return=total_return,
            annual_return=annual_return,
            monthly_returns=monthly_returns,
            volatility=volatility,
            max_drawdown=max_dd,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            profit_factor=profit_factor,
            avg_trade_return=avg_trade_return,
            best_day=best_day,
            worst_day=worst_day,
        )
