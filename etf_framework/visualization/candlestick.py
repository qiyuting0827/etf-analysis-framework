"""
Candlestick chart visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
from etf_framework.visualization.base import Visualizer
import logging

logger = logging.getLogger(__name__)


class CandlestickChart(Visualizer):
    """
    Candlestick chart visualization
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        title: str = "Candlestick Chart",
        figsize: tuple = (14, 7),
        width: float = 0.6,
    ):
        """
        Initialize candlestick chart
        
        Args:
            data: OHLCV data
            title: Chart title
            figsize: Figure size
            width: Candlestick width
        """
        super().__init__(title, figsize)
        self.data = data
        self.width = width
    
    def plot(self, save_path: str = None):
        """
        Generate candlestick chart
        
        Args:
            save_path: Path to save chart
        """
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Colors
        up_color = 'green'
        down_color = 'red'
        
        # Plot candlesticks
        for i, (idx, row) in enumerate(self.data.iterrows()):
            open_price = row['open']
            close_price = row['close']
            high_price = row['high']
            low_price = row['low']
            
            # Determine color
            if close_price >= open_price:
                color = up_color
                body_height = close_price - open_price
                body_bottom = open_price
            else:
                color = down_color
                body_height = open_price - close_price
                body_bottom = close_price
            
            # Wick
            ax.plot([i, i], [low_price, high_price], color=color, linewidth=1)
            
            # Body
            rect = Rectangle(
                (i - self.width / 2, body_bottom),
                self.width,
                body_height,
                facecolor=color,
                edgecolor=color,
            )
            ax.add_patch(rect)
        
        # Formatting
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title(self.title)
        ax.grid(True, alpha=0.3)
        
        # X-axis labels
        step = max(1, len(self.data) // 10)
        ax.set_xticks(range(0, len(self.data), step))
        ax.set_xticklabels(
            [self.data.index[i].strftime('%Y-%m-%d') for i in range(0, len(self.data), step)],
            rotation=45
        )
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        return fig, ax
