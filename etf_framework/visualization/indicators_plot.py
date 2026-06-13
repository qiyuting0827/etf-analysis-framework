"""
Technical indicators visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from etf_framework.visualization.base import Visualizer
import logging

logger = logging.getLogger(__name__)


class IndicatorPlotter(Visualizer):
    """
    Plot technical indicators
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        indicators: Dict[str, np.ndarray] = None,
        title: str = "Indicators",
        figsize: tuple = (14, 8),
    ):
        """
        Initialize indicator plotter
        
        Args:
            data: OHLCV data
            indicators: Dictionary of indicator name -> values
            title: Chart title
            figsize: Figure size
        """
        super().__init__(title, figsize)
        self.data = data
        self.indicators = indicators or {}
    
    def add_indicator(self, name: str, values: np.ndarray):
        """
        Add indicator to plot
        
        Args:
            name: Indicator name
            values: Indicator values
        """
        self.indicators[name] = values
    
    def plot(self, save_path: str = None):
        """
        Generate indicator plot
        
        Args:
            save_path: Path to save chart
        """
        num_subplots = 2  # Price + indicators
        fig, axes = plt.subplots(num_subplots, 1, figsize=self.figsize, sharex=True)
        
        # Plot price
        axes[0].plot(self.data.index, self.data['close'], label='Close', linewidth=2)
        axes[0].set_ylabel('Price')
        axes[0].set_title(self.title)
        axes[0].legend(loc='upper left')
        axes[0].grid(True, alpha=0.3)
        
        # Plot indicators
        for name, values in self.indicators.items():
            axes[1].plot(self.data.index, values, label=name, linewidth=1.5)
        
        axes[1].set_xlabel('Date')
        axes[1].set_ylabel('Indicator Value')
        axes[1].legend(loc='upper left')
        axes[1].grid(True, alpha=0.3)
        
        # Format x-axis
        step = max(1, len(self.data) // 10)
        axes[1].set_xticks(range(0, len(self.data), step))
        axes[1].set_xticklabels(
            [self.data.index[i].strftime('%Y-%m-%d') for i in range(0, len(self.data), step)],
            rotation=45
        )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        return fig, axes
