"""
Configuration settings
"""

import os
from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).parent.parent

# Data settings
DATA_DIR = PROJECT_ROOT / 'data'
CACHE_DIR = PROJECT_ROOT / '.cache'
CACHE_DIR.mkdir(exist_ok=True)

# Logging
LOG_DIR = PROJECT_ROOT / 'logs'
LOG_DIR.mkdir(exist_ok=True)
LOG_LEVEL = 'INFO'

# Backtest settings
DEFAULT_INITIAL_CAPITAL = 100000
DEFAULT_COMMISSION = 0.001  # 0.1%
DEFAULT_SLIPPAGE = 0.0005   # 0.05%

# Data provider settings
YAHOO_FINANCE_TIMEOUT = 30  # seconds

# Optimization settings
OPTIMIZATION_WORKERS = 4
OPTIMIZATION_TIMEOUT = 600  # seconds

# Visualization
DEFAULT_FIGSIZE = (14, 7)
DEFAULT_DPI = 100

# Risk-free rate (annual)
RISK_FREE_RATE = 0.02

# Trading periods per year
PERIODS_PER_YEAR = 252
