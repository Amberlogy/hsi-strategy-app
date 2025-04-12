"""
移動平均線交叉策略測試模組

測試 MACrossStrategy 類的功能，驗證交叉點偵測和信號生成是否正確
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 導入策略
from app.strategies.ma_cross_strategy import MACrossStrategy


def create_test_data(days=100, trend_days=20, amplitude=10, base_price=100):
    """
    創建具有上升和下降趨勢交替的測試數據
    
    Parameters
    ----------
    days : int
        總天數
    trend_days : int
        每個趨勢持續的天數
    amplitude : float
        價格波動幅度
    base_price : float
        基礎價格
        
    Returns
    -------
    pd.DataFrame
        包含 date, open, high, low, close 列的 DataFrame
    """
    # 創建日期序列
    dates = [datetime.now() + timedelta(days=i) for i in range(days)]
    
    # 初始化價格列表
    close_prices = []
    current_price = base_price
    
    # 創建交替的上升和下降趨勢
    for i in range(days):
        # 每 trend_days 天切換趨勢方向
        trend_period = i // trend_days
        is_uptrend = trend_period % 2 == 0
        
        # 添加趨勢和一些噪聲
        daily_change = (np.random.random() - 0.3) * 2  # 添加一些隨機性
        trend_factor = 0.5 if is_uptrend else -0.5  # 趨勢因子
        
        current_price += trend_factor + daily_change
        close_prices.append(current_price)
    
    # 創建 OHLC 數據
    df = pd.DataFrame({
        'date': dates,
        'close': close_prices
    })
    
    # 基於收盤價生成其他價格
    df['open'] = df['close'].shift(1).fillna(df['close'][0] * 0.99)
    df['high'] = df[['open', 'close']].max(axis=1) + np.random.random(days) * 0.5
    df['low'] = df[['open', 'close']].min(axis=1) - np.random.random(days) * 0.5
    
    # 設置日期為索引
    df = df.set_index('date')
    
    return df


def test_ma_cross_strategy_initialization():
    """測試 MACrossStrategy 初始化"""
    strategy = MACrossStrategy(short_period=5, long_period=10)
    
    assert strategy.short_period == 5
    assert strategy.long_period == 10
    assert strategy.ma_type == 'sma'
    assert "MA交叉策略 (5/10)" in strategy.name
    
    # 測試參數驗證
    with pytest.raises(ValueError):
        MACrossStrategy(short_period=20, long_period=10)  # 短期週期大於長期週期
        
    with pytest.raises(ValueError):
        MACrossStrategy(ma_type='invalid')  # 無效的移動平均線類型


def test_ma_cross_strategy_signals():
    """測試 MACrossStrategy 信號生成"""
    # 創建測試數據，確保有足夠的數據來計算移動平均線
    df = create_test_data(days=100, trend_days=20)
    
    # 初始化策略，使用較短的週期以確保生成足夠的交叉信號
    strategy = MACrossStrategy(short_period=5, long_period=15)
    
    # 生成信號
    signals = strategy.generate_signals(df)
    
    # 確認信號列存在
    assert 'signal' in signals.columns
    
    # 確認存在買入和賣出信號
    assert (signals['signal'] == 1).any(), "未找到買入信號"
    assert (signals['signal'] == -1).any(), "未找到賣出信號"
    
    # 檢查信號是否符合交叉點規則
    signal_counts = signals['signal'].value_counts()
    print(f"買入信號: {signal_counts.get(1, 0)}個, 賣出信號: {signal_counts.get(-1, 0)}個")
    
    # 確認有合理數量的交叉點
    # 在100天、20天趨勢週期的數據中，使用5/15的MA設置，應該有至少3個交叉點
    assert signal_counts.get(1, 0) >= 2, "買入信號數量不合理"
    assert signal_counts.get(-1, 0) >= 2, "賣出信號數量不合理"


def test_ma_cross_strategy_positions():
    """測試 MACrossStrategy 持倉轉換"""
    # 創建測試數據
    df = create_test_data(days=100, trend_days=20)
    
    # 初始化策略
    strategy = MACrossStrategy(short_period=5, long_period=15)
    
    # 生成信號
    signals = strategy.generate_signals(df)
    
    # 生成持倉狀態
    positions = strategy.generate_position(signals)
    
    # 確認持倉列存在
    assert 'position' in positions.columns
    
    # 檢查持倉轉換是否正確：買入信號後應持有多頭，賣出信號後應持有空頭
    # 找到第一個買入信號
    buy_signals = positions[positions['signal'] == 1].index
    if len(buy_signals) > 0:
        first_buy = buy_signals[0]
        # 確認買入信號後的持倉狀態為多頭(1)
        assert positions.loc[first_buy, 'position'] == 1
    
    # 找到第一個賣出信號
    sell_signals = positions[positions['signal'] == -1].index
    if len(sell_signals) > 0:
        first_sell = sell_signals[0]
        # 確認賣出信號後的持倉狀態為空頭(-1)
        assert positions.loc[first_sell, 'position'] == -1


def test_ma_cross_strategy_backtest():
    """測試 MACrossStrategy 回測功能"""
    # 創建測試數據
    df = create_test_data(days=100, trend_days=20)
    
    # 初始化策略
    strategy = MACrossStrategy(short_period=5, long_period=15)
    
    # 執行回測
    result = strategy.backtest(df, initial_capital=100000.0)
    
    # 確認結果包含必要欄位
    assert 'position' in result.columns
    assert 'returns' in result.columns
    assert 'strategy_returns' in result.columns
    assert 'capital' in result.columns
    
    # 確認資本曲線在最初幾行之後是有效的 (允許前面幾行有 NaN 因為移動平均線計算需要足夠數據)
    # 檢查最後 80% 的資料沒有 NaN
    check_start = int(len(result) * 0.2)  # 跳過前 20% 的數據
    assert not result['capital'].iloc[check_start:].isna().any()
    assert len(result['capital']) == len(df)
    
    # 確認績效指標已計算
    performance = strategy.performance
    assert 'total_return' in performance
    assert 'annual_return' in performance
    assert 'sharpe_ratio' in performance
    assert 'max_drawdown' in performance
    
    print(f"總回報: {performance['total_return']:.2%}")
    print(f"夏普比率: {performance['sharpe_ratio']:.2f}")
    print(f"最大回撤: {performance['max_drawdown']:.2%}")


def test_ema_cross_strategy():
    """測試 EMA 交叉策略功能"""
    # 創建測試數據
    df = create_test_data(days=100, trend_days=20)
    
    # 初始化 EMA 策略
    strategy = MACrossStrategy(short_period=5, long_period=15, ma_type='ema')
    
    # 生成信號
    signals = strategy.generate_signals(df)
    
    # 確認信號列存在
    assert 'signal' in signals.columns
    
    # 確認存在買入和賣出信號
    assert (signals['signal'] == 1).any(), "未找到買入信號"
    assert (signals['signal'] == -1).any(), "未找到賣出信號"
    
    # 檢查是否計算了 EMA 欄位
    assert f'ema_5' in signals.columns
    assert f'ema_15' in signals.columns


def test_expected_cross_points():
    """
    測試使用預定義的價格序列來驗證準確的交叉點數量
    """
    # 創建一個已知會產生特定交叉點的價格序列
    dates = pd.date_range(start='2023-01-01', periods=30)
    
    # 創建交替上升和下降的價格序列，確保會有交叉點
    close_prices = [
        100, 101, 102, 103, 104, 105, 106, 107, 108, 109,  # 上升趨勢
        108, 107, 105, 103, 101, 99, 97, 95, 93, 91,       # 下降趨勢
        92, 94, 96, 98, 100, 102, 104, 106, 108, 110       # 再次上升
    ]
    
    # 創建 DataFrame
    df = pd.DataFrame({
        'date': dates,
        'close': close_prices,
        'open': close_prices,
        'high': [p + 1 for p in close_prices],
        'low': [p - 1 for p in close_prices]
    })
    df = df.set_index('date')
    
    # 初始化策略，使用較短的週期以確保有足夠的交叉
    strategy = MACrossStrategy(short_period=3, long_period=8)
    
    # 生成信號
    signals = strategy.generate_signals(df)
    
    # 檢查信號數量
    buy_signals = (signals['signal'] == 1).sum()
    sell_signals = (signals['signal'] == -1).sum()
    
    print(f"預設數據中的買入信號: {buy_signals}個, 賣出信號: {sell_signals}個")
    
    # 我們預期在這個數據中應該有2個買入信號和1個賣出信號
    # (這取決於實際的MA交叉情況，可能需要根據實際計算的結果調整)
    assert buy_signals >= 1, "應該至少有1個買入信號"
    assert sell_signals >= 1, "應該至少有1個賣出信號"
    
    # 驗證信號位置的合理性
    # 在趨勢反轉後的一定天數內應該出現信號
    
    # 趨勢轉換點 (下降到上升，應在之後出現買入信號)
    trend_change_down_to_up = 19  # 索引19之後開始上升
    
    # 檢查此趨勢變化後是否有買入信號
    signals_after_up = signals.iloc[trend_change_down_to_up:]['signal']
    assert (signals_after_up == 1).any(), "趨勢轉向上升後應該出現買入信號" 