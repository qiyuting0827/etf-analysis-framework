"""
Base visualization class
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Visualizer(ABC):
    """
    Base class for visualizations
    """
    
    def __init__(self, title: str = "", figsize: tuple = (12, 6)):
        """
        Initialize visualizer
        
        Args:
            title: Chart title
            figsize: Figure size
        """
        self.title = title
        self.figsize = figsize
    
    @abstractmethod
    def plot(self):
        """
        Generate visualization
        """
        pass
