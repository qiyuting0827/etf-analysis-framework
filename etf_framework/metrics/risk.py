"""
Risk metrics calculation
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class RiskMetrics:
    """
    Calculate risk-related metrics
    """
    
    @staticmethod
    def calculate_volatility(
        returns: np.ndarray,
        periods_per_year: int = 252,
    ) -> float:
        """
        Calculate annualized volatility
        
        Args:
            returns: Daily returns
            periods_per_year: Trading periods per year
            
        Returns:
            Annualized volatility
        """
        return np.std(returns) * np.sqrt(periods_per_year)
    
    @staticmethod
    def calculate_var(
        returns: np.ndarray,
        confidence_level: float = 0.95,
    ) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Returns array
            confidence_level: Confidence level (0-1)
            
        Returns:
            VaR (negative value)
        """
        return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def calculate_cvar(
        returns: np.ndarray,
        confidence_level: float = 0.95,
    ) -> float:
        """
        Calculate Conditional Value at Risk (CVaR)
        
        Args:
            returns: Returns array
            confidence_level: Confidence level (0-1)
            
        Returns:
            CVaR
        """
        var = RiskMetrics.calculate_var(returns, confidence_level)
        return np.mean(returns[returns <= var])
    
    @staticmethod
    def calculate_beta(
        asset_returns: np.ndarray,
        market_returns: np.ndarray,
    ) -> float:
        """
        Calculate Beta (systematic risk)
        
        Args:
            asset_returns: Asset returns
            market_returns: Market returns
            
        Returns:
            Beta
        """
        covariance = np.cov(asset_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        
        if market_variance == 0:
            return 0.0
        
        return covariance / market_variance
    
    @staticmethod
    def calculate_alpha(
        asset_return: float,
        beta: float,
        market_return: float,
        risk_free_rate: float = 0.02,
    ) -> float:
        """
        Calculate Alpha (excess return)
        
        Args:
            asset_return: Asset annual return
            beta: Asset beta
            market_return: Market annual return
            risk_free_rate: Risk-free rate
            
        Returns:
            Alpha
        """
        expected_return = risk_free_rate + beta * (market_return - risk_free_rate)
        return asset_return - expected_return
    
    @staticmethod
    def calculate_recovery_factor(
        total_return: float,
        max_drawdown: float,
    ) -> float:
        """
        Calculate Recovery Factor (Total Return / Max Drawdown)
        
        Args:
            total_return: Total return
            max_drawdown: Maximum drawdown (negative value)
            
        Returns:
            Recovery factor
        """
        if max_drawdown == 0:
            return 0.0
        
        return total_return / abs(max_drawdown)
    
    @staticmethod
    def calculate_ulcer_index(
        returns: np.ndarray,
        window: int = 252,
    ) -> float:
        """
        Calculate Ulcer Index (measure of downside volatility)
        
        Args:
            returns: Daily returns
            window: Rolling window size
            
        Returns:
            Ulcer index
        """
        cumulative = np.cumprod(1 + returns) - 1
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / (running_max + 1)
        
        return np.sqrt(np.mean(drawdown ** 2))
