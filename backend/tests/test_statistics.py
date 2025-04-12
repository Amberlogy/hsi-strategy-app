"""
策略統計模組測試

測試策略績效評估功能
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.strategies.statistics import evaluate_strategy, calculate_max_drawdown, calculate_win_rate


def create_test_data():
    """創建測試用的策略回測結果數據"""
    # 創建日期範圍
    dates = pd.date_range(start='2023-01-01', periods=100)
    
    # 模擬資本曲線：從 100000 開始，有一些上漲和下跌
    initial_capital = 100000.0
    np.random.seed(42)  # 為了結果可重複
    
    # 創建回報率數據 (正態分佈，均值0.001，標準差0.02)
    returns = np.random.normal(0.001, 0.02, 100)
    
    # 創建模擬的交易信號 (1=多頭, -1=空頭, 0=不交易)
    # 讓我們假設每10天切換一次持倉方向
    position = np.zeros(100)
    for i in range(10):
        if i % 2 == 0:
            position[i*10:(i+1)*10] = 1  # 多頭
        else:
            position[i*10:(i+1)*10] = -1  # 空頭
    
    # 計算策略回報 (根據前一天的持倉和當天的回報)
    strategy_returns = position * returns
    
    # 計算累積資本 (從初始資本開始)
    capital = initial_capital * (1 + strategy_returns).cumprod()
    
    # 創建 DataFrame
    df = pd.DataFrame({
        'position': position,
        'returns': returns,
        'strategy_returns': strategy_returns,
        'capital': capital
    }, index=dates)
    
    return df


def test_evaluate_strategy():
    """測試評估策略函數"""
    # 創建測試數據
    df = create_test_data()
    
    # 計算績效指標
    performance = evaluate_strategy(df)
    
    # 驗證返回值是否包含所需的所有指標
    assert 'total_return' in performance
    assert 'annual_return' in performance
    assert 'max_drawdown' in performance
    assert 'trade_count' in performance
    assert 'win_rate' in performance
    assert 'sharpe_ratio' in performance
    assert 'volatility' in performance
    
    # 驗證總回報率計算是否正確
    expected_total_return = (df['capital'].iloc[-1] / df['capital'].iloc[0]) - 1
    assert abs(performance['total_return'] - expected_total_return) < 1e-10
    
    # 驗證交易次數計算是否正確
    # 交易次數應該是持倉發生變化的次數
    position_changes = df['position'].diff().fillna(0)
    expected_trade_count = (position_changes != 0).sum()
    assert performance['trade_count'] == expected_trade_count


def test_calculate_max_drawdown():
    """測試計算最大回撤函數"""
    # 創建一個簡單的報酬率序列
    returns = pd.Series([0.01, 0.02, -0.03, -0.02, 0.01, 0.03, -0.05, 0.04])
    
    # 計算最大回撤
    max_dd = calculate_max_drawdown(returns)
    
    # 手動計算的期望值
    wealth_index = (1 + returns).cumprod()
    previous_peaks = wealth_index.cummax()
    expected_drawdowns = (previous_peaks - wealth_index) / previous_peaks
    expected_max_dd = expected_drawdowns.max()
    
    # 驗證計算結果
    assert abs(max_dd - expected_max_dd) < 1e-10


def test_calculate_win_rate():
    """測試計算勝率函數"""
    # 創建測試數據
    signals = pd.Series([1, 1, 1, -1, -1, 0, 1, -1])
    returns = pd.Series([0.02, -0.01, 0.03, 0.01, -0.02, 0.01, -0.03, 0.02])
    
    # 計算勝率
    win_rate = calculate_win_rate(signals, returns)
    
    # 手動計算期望值
    strategy_returns = signals * returns
    trades = strategy_returns[signals != 0]
    expected_win_rate = (trades > 0).sum() / len(trades)
    
    # 驗證計算結果
    assert abs(win_rate - expected_win_rate) < 1e-10


def test_empty_dataframe():
    """測試空DataFrame的處理"""
    # 創建空的DataFrame，但包含所需的列
    df = pd.DataFrame(columns=['position', 'returns', 'strategy_returns', 'capital'])
    
    # 計算績效指標
    performance = evaluate_strategy(df)
    
    # 驗證所有指標都是零
    assert performance['total_return'] == 0.0
    assert performance['annual_return'] == 0.0
    assert performance['max_drawdown'] == 0.0
    assert performance['trade_count'] == 0
    assert performance['win_rate'] == 0.0
    assert performance['sharpe_ratio'] == 0.0
    assert performance['volatility'] == 0.0 