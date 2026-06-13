"""
Optimization analyzer
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationStats:
    """Optimization statistics"""
    total_trials: int
    best_score: float
    best_params: Dict[str, Any]
    mean_score: float
    std_score: float
    min_score: float
    max_score: float
    
    def summary(self) -> str:
        """Get summary"""
        return f"""
Optimization Statistics
{'='*50}
Total Trials:    {self.total_trials}
Best Score:      {self.best_score:.4f}
Mean Score:      {self.mean_score:.4f}
Std Dev:         {self.std_score:.4f}
Min Score:       {self.min_score:.4f}
Max Score:       {self.max_score:.4f}

Best Parameters:
{chr(10).join(f'  {k}: {v}' for k, v in self.best_params.items())}
"""


class OptimizationAnalyzer:
    """
    Analyze optimization results
    """
    
    @staticmethod
    def analyze(results: List[Dict]) -> OptimizationStats:
        """
        Analyze optimization results
        
        Args:
            results: List of results from optimization
            
        Returns:
            OptimizationStats
        """
        scores = [result['score'] for result in results]
        
        best_idx = np.argmax(scores)
        best_result = results[best_idx]
        
        return OptimizationStats(
            total_trials=len(results),
            best_score=float(np.max(scores)),
            best_params=best_result['params'],
            mean_score=float(np.mean(scores)),
            std_score=float(np.std(scores)),
            min_score=float(np.min(scores)),
            max_score=float(np.max(scores)),
        )
    
    @staticmethod
    def get_top_results(
        results: List[Dict],
        top_n: int = 10,
    ) -> List[Dict]:
        """
        Get top N results
        
        Args:
            results: Optimization results
            top_n: Number of top results
            
        Returns:
            Top results sorted by score
        """
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        return sorted_results[:top_n]
    
    @staticmethod
    def parameter_sensitivity(
        results: List[Dict],
        param_name: str,
    ) -> pd.DataFrame:
        """
        Analyze parameter sensitivity
        
        Args:
            results: Optimization results
            param_name: Parameter to analyze
            
        Returns:
            Sensitivity analysis DataFrame
        """
        df_results = []
        for result in results:
            param_value = result['params'].get(param_name)
            score = result['score']
            df_results.append({'parameter': param_value, 'score': score})
        
        df = pd.DataFrame(df_results)
        return df.groupby('parameter')['score'].agg(['mean', 'std', 'count']).reset_index()
