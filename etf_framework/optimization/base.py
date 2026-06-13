"""
Base optimizer class
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Callable, Tuple, Optional
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Optimization result"""
    best_params: Dict[str, Any]
    best_score: float
    all_results: List[Dict]
    history: List[Tuple[Dict, float]]
    
    def summary(self) -> str:
        """Get summary string"""
        return f"""
Optimization Results
{'='*50}
Best Parameters: {self.best_params}
Best Score:      {self.best_score:.4f}
Total Trials:    {len(self.all_results)}
"""


class Optimizer(ABC):
    """
    Base optimizer class
    """
    
    def __init__(self, name: str, **kwargs):
        """
        Initialize optimizer
        
        Args:
            name: Optimizer name
            **kwargs: Configuration
        """
        self.name = name
        self.config = kwargs
        self.best_params = None
        self.best_score = float('-inf')
        self.history: List[Tuple[Dict, float]] = []
    
    @abstractmethod
    def optimize(
        self,
        objective_func: Callable,
        param_space: Dict[str, List[Any]],
        maximize: bool = True,
    ) -> OptimizationResult:
        """
        Run optimization
        
        Args:
            objective_func: Objective function to optimize
            param_space: Parameter search space
            maximize: Maximize or minimize
            
        Returns:
            OptimizationResult
        """
        pass
    
    def _evaluate_objective(
        self,
        objective_func: Callable,
        params: Dict[str, Any],
    ) -> float:
        """
        Evaluate objective function
        
        Args:
            objective_func: Objective function
            params: Parameters to test
            
        Returns:
            Score
        """
        try:
            score = objective_func(**params)
            return float(score)
        except Exception as e:
            logger.error(f"Error evaluating params {params}: {str(e)}")
            return float('-inf')
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
