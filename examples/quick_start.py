"""
Quick start example - basic usage of the framework
"""

import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Import framework components
from etf_framework.data.loader import DataLoader
from etf_framework.data.yahoo_provider import YahooFinanceProvider
from etf_framework.strategies.examples.moving_average import MovingAverageCrossover
from etf_framework.backtest.engine import BacktestEngine, BacktestConfig
from etf_framework.metrics.analyzer import MetricsAnalyzer
from etf_framework.visualization.candlestick import CandlestickChart
from etf_framework.visualization.performance import PerformancePlotter


def main():
    """
    Quick start example
    """
    print("="*60)
    print("ETF Analysis Framework - Quick Start Example")
    print("="*60)
    
    # 1. Load data
    print("\n1. Loading data...")
    loader = DataLoader(provider=YahooFinanceProvider())
    data = loader.load(
        symbol='SPY',
        start_date='2022-01-01',
        end_date='2023-12-31',
        interval='1d'
    )
    
    if data.empty:
        print("Failed to load data. Please check your internet connection.")
        return
    
    print(f"Loaded {len(data)} bars of data")
    print(f"Date range: {data.index[0]} to {data.index[-1]}")
    
    # 2. Create strategy
    print("\n2. Creating strategy...")
    strategy = MovingAverageCrossover(
        short_period=20,
        long_period=50,
        use_ema=False
    )
    print(f"Strategy: {strategy}")
    
    # 3. Setup backtest
    print("\n3. Setting up backtest...")
    config = BacktestConfig(
        initial_capital=100000,
        commission=0.001,
        slippage=0.0005
    )
    engine = BacktestEngine(config=config)
    
    # 4. Run backtest
    print("\n4. Running backtest...")
    strategy.data = data
    strategy.setup()
    
    results = engine.run(data, strategy)
    
    # 5. Print results
    print("\n5. Backtest Results:")
    print("-" * 60)
    print(f"Initial Capital:     ${config.initial_capital:,.2f}")
    print(f"Final Capital:       ${results.final_capital:,.2f}")
    print(f"Total Return:        {results.total_return:.2%}")
    print(f"Total Trades:        {results.total_trades}")
    print(f"Winning Trades:      {results.winning_trades}")
    print(f"Losing Trades:       {results.losing_trades}")
    print(f"Win Rate:            {results.win_rate:.2%}")
    print(f"Profit Factor:       {results.profit_factor:.2f}")
    
    # 6. Analyze metrics
    print("\n6. Analyzing metrics...")
    equity_array = np.array(results.equity_curve)
    returns = np.diff(equity_array) / equity_array[:-1]
    
    analysis = MetricsAnalyzer.analyze(
        data=data,
        trades=results.trades,
        equity_curve=results.equity_curve,
        initial_capital=config.initial_capital,
    )
    
    print(analysis.summary())
    
    # 7. Save visualization
    print("\n7. Generating visualizations...")
    
    # Candlestick chart
    chart = CandlestickChart(data[-100:])  # Last 100 days
    chart.plot(save_path='candlestick.png')
    print("Saved candlestick chart to candlestick.png")
    
    # Performance plot
    perf_plot = PerformancePlotter(
        equity_curve=np.array(results.equity_curve),
        trades=results.trades,
        initial_capital=config.initial_capital,
    )
    perf_plot.plot(save_path='performance.png')
    print("Saved performance chart to performance.png")
    
    print("\n" + "="*60)
    print("Example completed!")
    print("="*60)


if __name__ == '__main__':
    main()
