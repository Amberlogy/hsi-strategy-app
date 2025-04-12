"""
策略績效統計模組

提供評估策略表現的各種指標計算功能
"""

import pandas as pd
import numpy as np
from typing import Dict, Any


def evaluate_strategy(df: pd.DataFrame) -> Dict[str, Any]:
    """
    評估策略績效
    
    計算策略的績效指標，包括總報酬率、最大回撤、交易次數、勝率等
    
    Parameters
    ----------
    df : pd.DataFrame
        回測結果的 DataFrame，必須包含以下欄位：
        - position: 持倉狀態
        - returns: 價格回報率
        - strategy_returns: 策略回報率
        - capital: 資本曲線
        
    Returns
    -------
    Dict[str, Any]
        包含各種績效指標的字典
    """
    # 驗證輸入 DataFrame 是否包含所需欄位
    required_columns = ['position', 'returns', 'strategy_returns', 'capital']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"輸入 DataFrame 必須包含 '{col}' 欄位")
    
    # 計算總報酬率 (最終資本 / 初始資本 - 1)
    if len(df) > 0:
        initial_capital = df['capital'].iloc[0]
        final_capital = df['capital'].iloc[-1]
        total_return = (final_capital / initial_capital) - 1
    else:
        total_return = 0.0
    
    # 計算年化報酬率
    if len(df) > 1:
        # 獲取第一天和最後一天的日期
        if isinstance(df.index, pd.DatetimeIndex):
            start_date = df.index[0]
            end_date = df.index[-1]
            days = (end_date - start_date).days
        else:
            # 如果索引不是日期型態，假設每行是一天
            days = len(df)
        
        # 計算年化報酬率 (假設一年有 252 個交易日)
        annual_return = (1 + total_return) ** (252 / max(days, 1)) - 1
    else:
        annual_return = 0.0
    
    # 計算最大回撤
    # 最大回撤是指資產從某個高點下跌到之後某個低點的最大幅度
    if len(df) > 0:
        # 計算資本的累積最大值
        running_max = df['capital'].cummax()
        
        # 計算回撤 = (累積最大值 - 當前值) / 累積最大值
        drawdown = (running_max - df['capital']) / running_max
        
        # 最大回撤是最大的回撤值
        max_drawdown = drawdown.max()
    else:
        max_drawdown = 0.0
    
    # 計算交易次數
    # 交易發生在 position 發生變化的地方
    if len(df) > 1:
        # 計算 position 的變化
        position_changes = df['position'].diff().fillna(0)
        
        # 交易次數是 position 變化不為 0 的次數
        trade_count = (position_changes != 0).sum()
    else:
        trade_count = 0
    
    # 計算勝率
    # 勝率是指盈利交易的數量佔總交易數量的比例
    if trade_count > 0:
        # 找出所有交易點
        trade_points = df[position_changes != 0].copy()
        
        # 計算每筆交易的盈虧
        trade_points['trade_profit'] = trade_points['strategy_returns']
        
        # 盈利交易的數量
        winning_trades = (trade_points['trade_profit'] > 0).sum()
        
        # 勝率
        win_rate = winning_trades / trade_count
    else:
        win_rate = 0.0
    
    # 計算夏普比率 (假設無風險利率為 2%)
    risk_free_rate = 0.02
    if len(df) > 1:
        # 計算策略回報的標準差 (年化)
        volatility = df['strategy_returns'].std() * np.sqrt(252)
        
        # 夏普比率 = (年化報酬率 - 無風險利率) / 年化標準差
        if volatility > 0:
            sharpe_ratio = (annual_return - risk_free_rate) / volatility
        else:
            sharpe_ratio = 0.0
    else:
        sharpe_ratio = 0.0
    
    # 計算收益波動率 (年化)
    if len(df) > 1:
        volatility = df['strategy_returns'].std() * np.sqrt(252)
    else:
        volatility = 0.0
    
    # 彙總所有指標
    performance = {
        'total_return': total_return,
        'annual_return': annual_return,
        'max_drawdown': max_drawdown,
        'trade_count': trade_count,
        'win_rate': win_rate,
        'sharpe_ratio': sharpe_ratio,
        'volatility': volatility
    }
    
    return performance


def calculate_max_drawdown(returns: pd.Series) -> float:
    """
    計算最大回撤
    
    Parameters
    ----------
    returns : pd.Series
        報酬率時間序列
        
    Returns
    -------
    float
        最大回撤值 (0 到 1 之間的值)
    """
    # 將報酬率轉換為資本曲線 (從 1 開始)
    wealth_index = (1 + returns).cumprod()
    
    # 計算歷史累積最大值
    previous_peaks = wealth_index.cummax()
    
    # 計算回撤
    drawdowns = (previous_peaks - wealth_index) / previous_peaks
    
    # 返回最大回撤
    return drawdowns.max()


def calculate_win_rate(signals: pd.Series, returns: pd.Series) -> float:
    """
    計算勝率
    
    Parameters
    ----------
    signals : pd.Series
        交易信號 (1 = 多頭, -1 = 空頭, 0 = 不交易)
    returns : pd.Series
        期間回報率
        
    Returns
    -------
    float
        勝率 (0 到 1 之間的值)
    """
    # 計算策略回報 (信號 * 回報率)
    strategy_returns = signals * returns
    
    # 找出交易點 (信號不為 0 的點)
    trades = strategy_returns[signals != 0]
    
    # 計算勝率
    if len(trades) > 0:
        win_rate = (trades > 0).sum() / len(trades)
    else:
        win_rate = 0.0
    
    return win_rate 