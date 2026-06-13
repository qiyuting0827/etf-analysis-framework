"""
Grid search optimization
"""

import numpy as np
from typing import Dict, List, Any, Callable, Tuple
from itertools import product
from etf_framework.optimization.base import Optimizer, OptimizationResult
import logging

logger = logging.getLogger(__name__)


class GridSearch(Optimizer):
    """
    Grid search optimization - exhaustive search over parameter space
    """
    
    def __init__(self, **kwargs):
        super().__init__(name='GridSearch', **kwargs)
    
    def optimize(
        self,
        objective_func: Callable,
        param_space: Dict[str, List[Any]],
        maximize: bool = True,
    ) -> OptimizationResult:
        """
        Run grid search optimization
        
        Args:
            objective_func: Objective function
            param_space: Parameter space
            maximize: Maximize or minimize
            
        Returns:
            OptimizationResult
        """
        logger.info("Starting grid search optimization")
        
        # Generate all parameter combinations
        param_names = list(param_space.keys())
        param_values = [param_space[name] for name in param_names]
        
        total_combinations = np.prod([len(v) for v in param_values])
        logger.info(f"Total parameter combinations: {total_combinations}")
        
        all_results = []
        best_score = float('-inf') if maximize else float('inf')
        best_params = None
        
        # Iterate through all combinations
        for i, combination in enumerate(product(*param_values)):
            params = dict(zip(param_names, combination))
            
            # Evaluate
            score = self._evaluate_objective(objective_func, params)
            all_results.append({'params': params, 'score': score})
            self.history.append((params.copy(), score))
            
            # Update best
            if maximize:
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
            else:
                if score < best_score:
                    best_score = score
                    best_params = params.copy()
            
            # Log progress
            if (i + 1) % max(1, total_combinations // 10) == 0:
                progress = (i + 1) / total_combinations * 100
                logger.info(f"Progress: {progress:.0f}% - Best Score: {best_score:.4f}")
        
        logger.info(f"Grid search completed. Best score: {best_score:.4f}")
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            history=self.history,
        )
