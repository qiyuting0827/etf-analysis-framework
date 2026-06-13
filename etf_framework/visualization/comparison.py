"""
Comparison visualization
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List
from etf_framework.visualization.base import Visualizer
import logging

logger = logging.getLogger(__name__)


class ComparisonPlotter(Visualizer):
    """
    Compare multiple strategies or assets
    """
    
    def __init__(
        self,
        title: str = "Strategy Comparison",
        figsize: tuple = (14, 7),
    ):
        """
        Initialize comparison plotter
        
        Args:
            title: Chart title
            figsize: Figure size
        """
        super().__init__(title, figsize)
        self.data: Dict[str, np.ndarray] = {}
    
    def add_series(self, name: str, values: np.ndarray):
        """
        Add series to compare
        
        Args:
            name: Series name
            values: Series values
        """
        self.data[name] = values
    
    def plot(self, save_path: str = None):
        """
        Generate comparison plot
        
        Args:
            save_path: Path to save chart
        """
        if not self.data:
            logger.warning("No data to plot")
            return None, None
        
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Normalize to 1.0 at start
        for name, values in self.data.items():
            normalized = values / values[0] if values[0] != 0 else values
            ax.plot(normalized, label=name, linewidth=2)
        
        ax.set_xlabel('Days')
        ax.set_ylabel('Normalized Return')
        ax.set_title(self.title)
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        return fig, ax
    
    def plot_metrics(
        self,
        metrics: Dict[str, Dict[str, float]],
        save_path: str = None,
    ):
        """
        Plot performance metrics comparison
        
        Args:
            metrics: Dict of strategy -> metrics
            save_path: Path to save chart
        """
        strategies = list(metrics.keys())
        metric_names = list(metrics[strategies[0]].keys())
        
        fig, axes = plt.subplots(2, 2, figsize=self.figsize)
        axes = axes.flatten()
        
        # Plot each metric
        for idx, metric_name in enumerate(metric_names[:4]):
            values = [metrics[s][metric_name] for s in strategies]
            axes[idx].bar(strategies, values, color='steelblue')
            axes[idx].set_title(metric_name)
            axes[idx].set_ylabel('Value')
            axes[idx].grid(True, alpha=0.3, axis='y')
            
            # Rotate x-axis labels
            axes[idx].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=100, bbox_inches='tight')
            logger.info(f"Chart saved to {save_path}")
        
        return fig, axes
