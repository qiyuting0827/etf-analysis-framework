"""
Performance visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from etf_framework.visualization.base import Visualizer
import logging

logger = logging.getLogger(__name__)


class PerformancePlotter(Visualizer):
    """
    Plot backtest performance
    """
    
    def __init__(
        self,
        equity_curve: np.ndarray,
        trades: list = None,
        initial_capital: float = 100000,
        title: str = "Performance",
        figsize: tuple = (14, 8),
    ):
        """
        Initialize performance plotter
        
        Args:
            equity_curve: Equity curve values
            trades: List of trades
            initial_capital: Initial capital
            title: Chart title
            figsize: Figure size
        """
        super().__init__(title, figsize)
        self.equity_curve = equity_curve
        self.trades = trades or []
        self.initial_capital = initial_capital
    
    def plot(self, save_path: str = None):
        """
        Generate performance plot
        
        Args:
            save_path: Path to save chart
        """
        fig, axes = plt.subplots(3, 1, figsize=self.figsize, sharex=True)
        
        # Equity curve
        axes[0].plot(self.equity_curve, linewidth=2, color='blue')
        axes[0].axhline(y=self.initial_capital, color='gray', linestyle='--', label='Initial Capital')
        axes[0].set_ylabel('Portfolio Value ($)')
        axes[0].set_title(self.title)
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # Drawdown
        peak = np.maximum.accumulate(self.equity_curve)
        drawdown = (self.equity_curve - peak) / peak * 100
        axes[1].fill_between(range(len(drawdown)), drawdown, 0, color='red', alpha=0.3)
        axes[1].plot(drawdown, color='red', linewidth=1)
        axes[1].set_ylabel('Drawdown (%)')
        axes[1].grid(True, alpha=0.3)
        
        # Daily returns
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1] * 100
        colors = ['green' if r > 0 else 'red' for r in returns]
        axes[2].bar(range(len(returns)), returns, color=colors, width=1)
        axes[2].set_xlabel('Days')
        axes[2].set_ylabel('Daily Return (%)')
        axes[2].grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        return fig, axes
