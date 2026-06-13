"""
Strategy optimization example
"""

import pandas as pd
import numpy as np
from etf_framework.data.loader import DataLoader
from etf_framework.data.yahoo_provider import YahooFinanceProvider
from etf_framework.strategies.examples.moving_average import MovingAverageCrossover
from etf_framework.backtest.engine import BacktestEngine, BacktestConfig
from etf_framework.optimization.grid_search import GridSearch
from etf_framework.optimization.analyzer import OptimizationAnalyzer


def objective_function(data, config, short_period, long_period):
    """
    Objective function for optimization
    
    Args:
        data: Historical data
        config: Backtest config
        short_period: Short MA period
        long_period: Long MA period
        
    Returns:
        Sharpe ratio (objective metric)
    """
    # Create strategy
    strategy = MovingAverageCrossover(
        short_period=int(short_period),
        long_period=int(long_period)
    )
    
    # Run backtest
    engine = BacktestEngine(config)
    results = engine.run(data, strategy)
    
    # Calculate Sharpe ratio as objective
    if len(results.equity_curve) == 0:
        return -100
    
    equity_array = np.array(results.equity_curve)
    returns = np.diff(equity_array) / equity_array[:-1]
    
    if np.std(returns) == 0:
        return 0
    
    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)
    return sharpe


def main():
    print("Strategy Optimization Example")
    print("="*60)
    
    # Load data
    loader = DataLoader(provider=YahooFinanceProvider())
    data = loader.load(
        symbol='QQQ',
        start_date='2022-01-01',
        end_date='2023-12-31'
    )
    
    if data.empty:
        print("Failed to load data")
        return
    
    print(f"Loaded {len(data)} bars")
    
    # Define parameter space
    param_space = {
        'short_period': [10, 15, 20, 25],
        'long_period': [40, 50, 60],
    }
    
    config = BacktestConfig(initial_capital=100000)
    
    # Create objective function with fixed parameters
    def obj_func(**params):
        return objective_function(data, config, **params)
    
    # Run optimization
    print("\nRunning grid search optimization...")
    optimizer = GridSearch()
    result = optimizer.optimize(
        objective_func=obj_func,
        param_space=param_space,
        maximize=True
    )
    
    # Analyze results
    print("\nOptimization Results:")
    print("-"*60)
    print(result.summary())
    
    # Get top 5 results
    analyzer = OptimizationAnalyzer()
    stats = analyzer.analyze(result.all_results)
    print(stats.summary())
    
    top_results = analyzer.get_top_results(result.all_results, top_n=5)
    print("\nTop 5 Results:")
    for i, res in enumerate(top_results, 1):
        print(f"  {i}. Params: {res['params']}, Score: {res['score']:.4f}")


if __name__ == '__main__':
    main()
