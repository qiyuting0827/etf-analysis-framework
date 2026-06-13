"""
Complete pipeline example - from data loading to analysis
"""

import pandas as pd
import numpy as np
from etf_framework.data.loader import DataLoader
from etf_framework.data.yahoo_provider import YahooFinanceProvider
from etf_framework.strategies.factory import StrategyFactory
from etf_framework.backtest.engine import BacktestEngine, BacktestConfig
from etf_framework.metrics.analyzer import MetricsAnalyzer
from etf_framework.visualization.performance import PerformancePlotter
from etf_framework.visualization.comparison import ComparisonPlotter


def run_strategy(data, strategy_name, strategy_params, config):
    """
    Run a strategy and return results
    
    Args:
        data: Price data
        strategy_name: Strategy name
        strategy_params: Strategy parameters
        config: Backtest config
        
    Returns:
        Results and analysis
    """
    # Create strategy
    strategy = StrategyFactory.create(strategy_name, **strategy_params)
    
    # Run backtest
    engine = BacktestEngine(config)
    results = engine.run(data, strategy)
    
    # Analyze
    analysis = MetricsAnalyzer.analyze(
        data=data,
        trades=results.trades,
        equity_curve=results.equity_curve,
        initial_capital=config.initial_capital,
    )
    
    return results, analysis


def main():
    print("Complete Pipeline Example")
    print("="*60)
    
    # 1. Load data
    print("\n1. Loading data...")
    loader = DataLoader(provider=YahooFinanceProvider())
    data = loader.load(
        symbol='SPY',
        start_date='2022-01-01',
        end_date='2023-12-31'
    )
    
    if data.empty:
        print("Failed to load data")
        return
    
    print(f"Loaded {len(data)} bars")
    
    # 2. Setup backtest config
    config = BacktestConfig(
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    
    # 3. Run multiple strategies
    print("\n2. Running strategies...")
    
    strategies = [
        ('MovingAverageCrossover', {'short_period': 20, 'long_period': 50}),
        ('RSI', {'period': 14, 'overbought': 70, 'oversold': 30}),
        ('MACD', {'fast': 12, 'slow': 26, 'signal_period': 9}),
    ]
    
    all_results = {}
    all_analysis = {}
    
    for strategy_name, params in strategies:
        print(f"  Running {strategy_name}...")
        results, analysis = run_strategy(data, strategy_name, params, config)
        all_results[strategy_name] = results
        all_analysis[strategy_name] = analysis
    
    # 4. Compare results
    print("\n3. Comparing strategies...")
    print("-"*60)
    print(f"{'Strategy':<25} {'Return':<12} {'Sharpe':<10} {'Win Rate':<10}")
    print("-"*60)
    
    for name, analysis in all_analysis.items():
        print(
            f"{name:<25} {analysis.total_return:>10.2%}  "
            f"{analysis.sharpe_ratio:>8.2f}  {analysis.win_rate:>8.2%}"
        )
    
    # 5. Visualize comparison
    print("\n4. Generating visualizations...")
    
    # Compare equity curves
    comp_plot = ComparisonPlotter(title="Strategy Comparison")
    for name, results in all_results.items():
        comp_plot.add_series(name, np.array(results.equity_curve))
    
    comp_plot.plot(save_path='comparison.png')
    print("Saved comparison chart to comparison.png")
    
    # Compare metrics
    metrics_dict = {}
    for name, analysis in all_analysis.items():
        metrics_dict[name] = {
            'Total Return': analysis.total_return,
            'Sharpe Ratio': analysis.sharpe_ratio,
            'Win Rate': analysis.win_rate,
            'Profit Factor': analysis.profit_factor,
        }
    
    comp_plot.plot_metrics(metrics_dict, save_path='metrics_comparison.png')
    print("Saved metrics comparison to metrics_comparison.png")
    
    # 6. Print detailed analysis
    print("\n5. Detailed Analysis for Best Strategy")
    print("-"*60)
    
    best_name = max(all_analysis.items(), key=lambda x: x[1].sharpe_ratio)[0]
    best_analysis = all_analysis[best_name]
    
    print(f"Best Strategy: {best_name}")
    print(best_analysis.summary())
    
    print("\n" + "="*60)
    print("Pipeline completed!")
    print("="*60)


if __name__ == '__main__':
    main()
