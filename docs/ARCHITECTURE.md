# ETF Analysis Framework - Architecture Documentation

## 系统架构概述

### 核心设计原则

1. **模块化设计** - 完全解耦，各模块独立且可复用
2. **可插拔架构** - 易于添加新指标、策略、优化器
3. **事件驱动** - 高效的异步处理机制
4. **工厂模式** - 统一的对象创建接口
5. **策略模式** - 灵活的算法替换

## 模块结构

### 1. 数据管理 (`data/`)

**职责**: 数据加载、缓存、预处理

```
DataProvider (ABC)
├── YahooFinanceProvider
├── TushareProvider
└── CustomProvider

DataLoader
├── 多数据源支持
├── 缓存机制
└── 自动预处理

DataCache
├── 内存缓存
├── 磁盘缓存
└── 缓存管理
```

**特性**:
- 支持多数据源（Yahoo Finance、Tushare等）
- 三层缓存体系（内存、磁盘、网络）
- 数据验证和清洗
- 异步加载支持

### 2. 技术指标 (`indicators/`)

**职责**: 指标计算和管理

```
Indicator (ABC)
├── MomentumIndicators
│   ├── RSI
│   ├── Stochastic
│   ├── MACD
│   ├── CCI
│   └── ROC
├── TrendIndicators
│   ├── SMA
│   ├── EMA
│   ├── WMA
│   ├── TEMA
│   └── ADX
├── VolatilityIndicators
│   ├── ATR
│   ├── BollingerBands
│   ├── KeltnerChannel
│   └── StdDev
└── VolumeIndicators
    ├── OBV
    ├── CMF
    └── VolumeROC

IndicatorRegistry
└── 工厂模式实现
```

**特性**:
- 30+内置指标
- 自定义指标支持
- 动态指标更新
- 指标链式计算

### 3. 交易策略 (`strategies/`)

**职责**: 策略定义和执行

```
Strategy (ABC)
├── setup() - 初始化
├── next() - 信号生成
├── add_indicator() - 添加指标
└── generate_signal() - 生成信号

StrategyFactory
├── MovingAverageCrossover
├── RSIStrategy
├── MACDStrategy
└── CustomStrategy
```

**特性**:
- 统一的策略接口
- 内置3+例子策略
- 轻量级信号管理
- 策略工厂模式

### 4. 回测引擎 (`backtest/`)

**职责**: 历史数据上的策略执行

```
BacktestEngine
├── run() - 主回测循环
├── _execute_signal() - 信号执行
├── _open_position() - 开仓
└── _close_position() - 平仓

Portfolio
├── buy() - 买入
├── sell() - 卖出
├── get_portfolio_value() - 组合估值
└── get_holdings() - 持仓查询

BacktestConfig
├── initial_capital
├── commission
├── slippage
└── position_size
```

**特性**:
- 事件驱动执行
- 精确的手续费和滑点模型
- 完整的交易记录
- 高效的回测性能

### 5. 性能评估 (`metrics/`)

**职责**: 性能指标计算和分析

```
PerformanceMetrics
├── Sharpe Ratio
├── Sortino Ratio
├── Calmar Ratio
├── Win Rate
├── Profit Factor
└── Max Drawdown

RiskMetrics
├── Volatility
├── VaR (Value at Risk)
├── CVaR (Conditional VaR)
├── Beta
├── Alpha
└── Ulcer Index

MetricsAnalyzer
└── 综合分析
```

**特性**:
- 20+性能指标
- 风险调整收益
- 月度/年度统计
- 完整的回撤分析

### 6. 策略优化 (`optimization/`)

**职责**: 参数优化和搜索

```
Optimizer (ABC)
├── GridSearch
│   └── 网格搜索
├── BayesianOptimizer
│   └── 贝叶斯优化
└── GeneticAlgorithm
    └── 遗传算法

OptimizationAnalyzer
├── 参数敏感性分析
├── 前5结果提取
└── 统计分析
```

**特性**:
- 3种优化算法
- 过度拟合检测
- 参数敏感性分析
- 完整的优化历史

### 7. 可视化 (`visualization/`)

**职责**: 图表和仪表板生成

```
Visualizer (ABC)
├── CandlestickChart - K线图
├── IndicatorPlotter - 指标图
├── PerformancePlotter - 性能图
├── ComparisonPlotter - 对比图
└── Dashboard - 仪表板
```

**特性**:
- Matplotlib/Plotly支持
- 交互式图表
- 多策略对比
- 自动保存功能

### 8. 工具库 (`utils/`)

**职责**: 通用工具和辅助函数

```
Decorators
├── @timer - 性能计时
├── @retry - 失败重试
└── @memoize - 结果缓存

Validators
├── validate_ohlcv() - 数据验证
└── validate_parameters() - 参数验证

Helpers
├── 日期处理
├── 数据格式化
├── 指标合并
└── 性能计算
```

## 数据流

```
┌─────────────┐
│  Data Load  │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Validation   │
└──────┬───────┘
       │
       ▼
┌──────────────┐      ┌────────────────┐
│   Cache      │─────▶│  Indicators    │
└──────┬───────┘      └────────┬───────┘
       │                       │
       │                       ▼
       │              ┌────────────────┐
       │              │   Strategy     │
       │              └────────┬───────┘
       │                       │
       ▼                       ▼
┌──────────────────────────────────┐
│     Backtest Engine              │
│  - Execute Signals               │
│  - Manage Portfolio              │
│  - Calculate P&L                 │
└──────────────────────────────────┘
       │
       ▼
┌──────────────┐
│  Metrics     │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│  Visualization & Reports     │
└──────────────────────────────┘
```

## 扩展性

### 添加新指标

```python
from etf_framework.indicators.base import Indicator, IndicatorType

class MyIndicator(Indicator):
    def _calculate(self, data):
        # 实现指标逻辑
        return result

# 注册
IndicatorRegistry.register('MyIndicator', MyIndicator)
```

### 添加新策略

```python
from etf_framework.strategies.base import Strategy

class MyStrategy(Strategy):
    def setup(self):
        # 初始化
        pass
    
    def next(self):
        # 生成信号
        return signal

# 注册
StrategyFactory.register('MyStrategy', MyStrategy)
```

### 添加新优化器

```python
from etf_framework.optimization.base import Optimizer

class MyOptimizer(Optimizer):
    def optimize(self, objective_func, param_space, maximize):
        # 优化逻辑
        return result
```

## 性能考虑

1. **缓存策略** - 多层缓存减少I/O
2. **向量化计算** - NumPy加速指标计算
3. **事件驱动** - 避免不必要的计算
4. **增量更新** - 支持实时数据更新
5. **并行处理** - 支持多策略并行优化

## 测试覆盖

- 单元测试 (`tests/test_*.py`)
- 集成测试
- 性能测试
- 回归测试

## 依赖管理

```
Core: pandas, numpy, scipy
Data: yfinance, tushare
Visualization: matplotlib, seaborn, plotly
Optimization: optuna, pygad
Logging: loguru
```
