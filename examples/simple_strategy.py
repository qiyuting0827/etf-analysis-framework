"""
Simple strategy example
"""

import pandas as pd
import numpy as np
from etf_framework.strategies.base import Strategy, Signal
from etf_framework.indicators.trend import SMA
from etf_framework.indicators.momentum import RSI
from etf_framework.backtest.engine import BacktestEngine, BacktestConfig
from etf_framework.data.loader import DataLoader
from etf_framework.data.yahoo_provider import YahooFinanceProvider


class SimpleStrategy(Strategy):
    """
    Simple strategy combining SMA and RSI
    """
    
    def __init__(self, sma_period=20, rsi_period=14, **kwargs):
        super().__init__(name='SimpleStrategy', **kwargs)
        self.sma_period = sma_period
        self.rsi_period = rsi_period
        self.sma = None
        self.rsi = None
    
    def setup(self):
        """Setup indicators"""
        self.sma = self.add_indicator('SMA', SMA(period=self.sma_period))
        self.rsi = self.add_indicator('RSI', RSI(period=self.rsi_period))
    
    def next(self) -> Signal:
        """Generate signals"""
        if self.data is None or self.current_index < max(self.sma_period, self.rsi_period):
            return None
        
        # Calculate indicators
        close_prices = self.data['close'].values[:self.current_index + 1]
        
        self.sma.calculate(close_prices)
        self.rsi.calculate(close_prices)
        
        if not (self.sma.is_ready and self.rsi.is_ready):
            return None
        
        current_price = close_prices[-1]
        sma_value = self.sma.current_value
        rsi_value = self.rsi.current_value
        
        # Buy signal: price above SMA and RSI < 70
        if current_price > sma_value and rsi_value < 70 and self.position == 0:
            return self.generate_signal(
                signal_type='buy',
                strength=0.7,
                reason=f'Price > SMA and RSI={rsi_value:.0f}',
                metadata={'sma': sma_value, 'rsi': rsi_value}
            )
        
        # Sell signal: price below SMA or RSI > 80
        elif (current_price < sma_value or rsi_value > 80) and self.position > 0:
            return self.generate_signal(
                signal_type='sell',
                strength=0.7,
                reason=f'Price < SMA or RSI={rsi_value:.0f}',
                metadata={'sma': sma_value, 'rsi': rsi_value}
            )
        
        return None


def main():
    print("Simple Strategy Example")
    print("="*60)
    
    # Load data
    loader = DataLoader(provider=YahooFinanceProvider())
    data = loader.load(
        symbol='AAPL',
        start_date='2023-01-01',
        end_date='2023-12-31'
    )
    
    if data.empty:
        print("Failed to load data")
        return
    
    print(f"Loaded {len(data)} bars")
    
    # Create strategy
    strategy = SimpleStrategy(sma_period=20, rsi_period=14)
    
    # Run backtest
    config = BacktestConfig(initial_capital=100000)
    engine = BacktestEngine(config)
    
    results = engine.run(data, strategy)
    
    # Print results
    print(f"\nResults:")
    print(f"Total Return: {results.total_return:.2%}")
    print(f"Trades: {results.total_trades}")
    print(f"Win Rate: {results.win_rate:.2%}")
    print(f"Profit Factor: {results.profit_factor:.2f}")


if __name__ == '__main__':
    main()
