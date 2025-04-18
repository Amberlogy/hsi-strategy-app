"""
策略模組包

包含各種交易策略實現
"""

from .strategy_base import StrategyBase
from .moving_average import calculate_sma, calculate_ema, detect_sma_cross
from .macd import calculate_macd, detect_macd_cross
from .ma_cross_strategy import MACrossStrategy

__all__ = [
    'StrategyBase',
    'calculate_sma',
    'calculate_ema',
    'detect_sma_cross',
    'calculate_macd',
    'detect_macd_cross',
    'MACrossStrategy'
] 