"""
測試 MA Cross 策略

此測試模組用於驗證移動平均線交叉策略的功能
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.strategies import MACrossStrategy


def generate_test_data(days=200, start_date='2023-01-01'):
    """生成測試用的股價數據"""
    # 創建日期範圍
    dates = pd.date_range(start=start_date, periods=days)
    
    # 生成模擬價格數據
    seed = 42
    np.random.seed(seed)
    
    # 起始價格
    start_price = 100
    
    # 生成價格向量 (隨機游走加上趨勢)
    price = start_price
    prices = [price]
    
    # 添加一些趨勢和噪聲
    for i in range(1, days):
        # 添加趨勢 (正向趨勢在前半部分，負向趨勢在後半部分)
        if i < days // 2:
            trend = 0.1  # 上升趨勢
        else:
            trend = -0.05  # 下降趨勢
            
        # 價格波動
        change = np.random.normal(trend, 1.0)
        price = max(price + change, 1.0)  # 確保價格不會低於1
        prices.append(price)
    
    # 建立 DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': prices,
        'high': [p * (1 + np.random.uniform(0, 0.02)) for p in prices],
        'low': [p * (1 - np.random.uniform(0, 0.02)) for p in prices],
        'close': [p * (1 + np.random.normal(0, 0.005)) for p in prices],
        'volume': [int(np.random.uniform(100000, 1000000)) for _ in range(days)]
    })
    
    return df


def test_ma_cross_strategy():
    """測試移動平均線交叉策略"""
    # 生成測試數據
    print("生成測試數據...")
    df = generate_test_data(days=200)
    
    # 創建策略實例
    print("\n創建策略實例...")
    strategy = MACrossStrategy(short_period=10, long_period=30)
    
    # 執行回測
    print(f"\n執行 {strategy.name} 回測...")
    results = strategy.run_backtest(df, initial_capital=100000.0, commission=0.001)
    
    # 輸出績效指標
    print("\n績效指標:")
    perf = results['performance']
    for key, value in perf.items():
        if isinstance(value, float):
            if 'rate' in key or 'return' in key:
                print(f"{key}: {value:.2%}")
            else:
                print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")
    
    # 繪製回測結果
    print("\n繪製回測結果...")
    strategy.plot_performance(results['positions'])
    
    return results


if __name__ == "__main__":
    print("開始測試移動平均線交叉策略...")
    test_ma_cross_strategy()
    print("\n測試完成!") 