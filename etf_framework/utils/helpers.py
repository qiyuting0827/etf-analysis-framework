"""
Helper functions
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def date_range(start_date: str, end_date: str, freq: str = 'D') -> List[str]:
    """
    Generate date range
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        freq: Frequency (D=daily, W=weekly, M=monthly)
        
    Returns:
        List of dates
    """
    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    return [d.strftime('%Y-%m-%d') for d in dates]


def calculate_ann_return(daily_returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate annualized return
    
    Args:
        daily_returns: Daily returns
        periods_per_year: Periods per year
        
    Returns:
        Annualized return
    """
    if len(daily_returns) == 0:
        return 0.0
    return np.prod(1 + daily_returns) ** (periods_per_year / len(daily_returns)) - 1


def calculate_ann_volatility(daily_returns: np.ndarray, periods_per_year: int = 252) -> float:
    """
    Calculate annualized volatility
    
    Args:
        daily_returns: Daily returns
        periods_per_year: Periods per year
        
    Returns:
        Annualized volatility
    """
    if len(daily_returns) == 0:
        return 0.0
    return np.std(daily_returns) * np.sqrt(periods_per_year)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value (0-1)
        decimals: Decimal places
        
    Returns:
        Formatted string
    """
    return f"{value * 100:.{decimals}f}%"


def format_currency(value: float, decimals: int = 2) -> str:
    """
    Format value as currency
    
    Args:
        value: Currency value
        decimals: Decimal places
        
    Returns:
        Formatted string
    """
    return f"${value:,.{decimals}f}"


def merge_indicators(data: pd.DataFrame, indicators: Dict[str, np.ndarray]) -> pd.DataFrame:
    """
    Merge indicators with OHLCV data
    
    Args:
        data: OHLCV data
        indicators: Dictionary of indicator name -> values
        
    Returns:
        Merged DataFrame
    """
    result = data.copy()
    for name, values in indicators.items():
        result[name] = values
    return result
