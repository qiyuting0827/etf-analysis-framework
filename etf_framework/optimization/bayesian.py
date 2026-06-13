"""
Bayesian optimization
"""

import numpy as np
from typing import Dict, List, Any, Callable, Tuple, Optional
from etf_framework.optimization.base import Optimizer, OptimizationResult
import logging

logger = logging.getLogger(__name__)


class BayesianOptimizer(Optimizer):
    """
    Bayesian optimization using Gaussian Process
    More efficient than grid search for high-dimensional spaces
    """
    
    def __init__(self, n_iterations: int = 50, **kwargs):
        """
        Initialize Bayesian optimizer
        
        Args:
            n_iterations: Number of iterations
            **kwargs: Additional config
        """
        super().__init__(name='BayesianOptimizer', **kwargs)
        self.n_iterations = n_iterations
    
    def optimize(
        self,
        objective_func: Callable,
        param_space: Dict[str, Tuple[float, float]],
        maximize: bool = True,
    ) -> OptimizationResult:
        """
        Run Bayesian optimization
        
        Args:
            objective_func: Objective function
            param_space: Parameter space with bounds (min, max)
            maximize: Maximize or minimize
            
        Returns:
            OptimizationResult
        """
        try:
            from optuna import create_study, Trial
            import optuna
        except ImportError:
            logger.error("Optuna required for Bayesian optimization")
            logger.info("Falling back to random search")
            return self._random_search(objective_func, param_space, maximize)
        
        logger.info("Starting Bayesian optimization with Optuna")
        
        all_results = []
        
        def optuna_objective(trial: Trial) -> float:
            params = {}
            for param_name, (min_val, max_val) in param_space.items():
                if isinstance(min_val, int):
                    params[param_name] = trial.suggest_int(param_name, min_val, max_val)
                else:
                    params[param_name] = trial.suggest_float(param_name, min_val, max_val)
            
            score = self._evaluate_objective(objective_func, params)
            all_results.append({'params': params, 'score': score})
            self.history.append((params.copy(), score))
            
            return score
        
        # Create study
        direction = 'maximize' if maximize else 'minimize'
        study = optuna.create_study(direction=direction)
        study.optimize(optuna_objective, n_trials=self.n_iterations, show_progress_bar=True)
        
        # Get best result
        best_trial = study.best_trial
        best_params = best_trial.params
        best_score = best_trial.value
        
        logger.info(f"Bayesian optimization completed. Best score: {best_score:.4f}")
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            history=self.history,
        )
    
    def _random_search(
        self,
        objective_func: Callable,
        param_space: Dict[str, Tuple[float, float]],
        maximize: bool = True,
    ) -> OptimizationResult:
        """
        Fallback random search
        """
        logger.info("Running random search")
        
        all_results = []
        best_score = float('-inf') if maximize else float('inf')
        best_params = None
        
        for i in range(self.n_iterations):
            params = {}
            for param_name, (min_val, max_val) in param_space.items():
                if isinstance(min_val, int):
                    params[param_name] = np.random.randint(min_val, max_val + 1)
                else:
                    params[param_name] = np.random.uniform(min_val, max_val)
            
            score = self._evaluate_objective(objective_func, params)
            all_results.append({'params': params, 'score': score})
            self.history.append((params.copy(), score))
            
            if maximize:
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
            else:
                if score < best_score:
                    best_score = score
                    best_params = params.copy()
        
        return OptimizationResult(
            best_params=best_params,
            best_score=best_score,
            all_results=all_results,
            history=self.history,
        )
