"""
技術指標計算模組
提供各種金融技術指標的計算函數
"""

import pandas as pd
import numpy as np
from typing import Union, Optional


def bollinger_bands(
    df: pd.DataFrame,
    period: int = 20,
    std_dev: int = 2,
    column: str = 'close'
) -> pd.DataFrame:
    """
    計算布林帶 (Bollinger Bands) 技術指標
    
    布林帶由三條線組成：
    - 中軌（SMA）：n 期簡單移動平均線
    - 上軌：中軌 + k 倍標準差
    - 下軌：中軌 - k 倍標準差
    - 帶寬：(上軌 - 下軌) / 中軌
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame，必須有指定的 column
    period : int, default 20
        移動平均的計算週期
    std_dev : int, default 2
        標準差乘數，一般為 2
    column : str, default 'close'
        用於計算的價格列名，默認為 'close' 收盤價
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上以下列:
        - bb_middle: 布林帶中軌 (SMA)
        - bb_upper: 布林帶上軌
        - bb_lower: 布林帶下軌
        - bb_width: 布林帶寬度
        
    Examples
    --------
    >>> import pandas as pd
    >>> data = pd.DataFrame({'close': [100, 101, 102, 101, 99, 98, 97, 96, 97, 98]})
    >>> result = bollinger_bands(data, period=5, std_dev=2)
    >>> print(result.tail())
    """
    
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 列")
    
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算中軌 (SMA)
    result['bb_middle'] = result[column].rolling(window=period).mean()
    
    # 計算標準差
    result['bb_std'] = result[column].rolling(window=period).std()
    
    # 計算上下軌
    result['bb_upper'] = result['bb_middle'] + (result['bb_std'] * std_dev)
    result['bb_lower'] = result['bb_middle'] - (result['bb_std'] * std_dev)
    
    # 計算帶寬
    result['bb_width'] = (result['bb_upper'] - result['bb_lower']) / result['bb_middle']
    
    # 移除臨時列
    result = result.drop('bb_std', axis=1)
    
    return result


def macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    column: str = 'close'
) -> pd.DataFrame:
    """
    計算 MACD (Moving Average Convergence Divergence) 指標
    
    MACD 由以下三個部分組成：
    - MACD 線：快速 EMA - 慢速 EMA
    - 信號線：MACD 線的 EMA
    - 柱狀圖：MACD 線 - 信號線
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame，必須有指定的 column
    fast_period : int, default 12
        快速 EMA 週期
    slow_period : int, default 26
        慢速 EMA 週期
    signal_period : int, default 9
        信號線 EMA 週期
    column : str, default 'close'
        用於計算的價格列名，默認為 'close' 收盤價
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上以下列:
        - macd: MACD 線
        - macd_signal: 信號線
        - macd_histogram: 柱狀圖
    """
    
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 列")
    
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算快速和慢速 EMA
    fast_ema = result[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = result[column].ewm(span=slow_period, adjust=False).mean()
    
    # 計算 MACD 線
    result['macd'] = fast_ema - slow_ema
    
    # 計算信號線
    result['macd_signal'] = result['macd'].ewm(span=signal_period, adjust=False).mean()
    
    # 計算柱狀圖
    result['macd_histogram'] = result['macd'] - result['macd_signal']
    
    return result


def rsi(
    df: pd.DataFrame,
    period: int = 14,
    column: str = 'close'
) -> pd.DataFrame:
    """
    計算 RSI (Relative Strength Index) 指標
    
    RSI = 100 - (100 / (1 + RS))
    其中 RS = 平均上漲 / 平均下跌
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame，必須有指定的 column
    period : int, default 14
        RSI 計算週期
    column : str, default 'close'
        用於計算的價格列名，默認為 'close' 收盤價
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上以下列:
        - rsi: RSI 值
    """
    
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 列")
    
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算價格變化
    delta = result[column].diff()
    
    # 分離上漲和下跌
    gain = delta.copy()
    loss = delta.copy()
    gain[gain < 0] = 0
    loss[loss > 0] = 0
    loss = abs(loss)
    
    # 計算平均上漲和下跌
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # 計算 RS 和 RSI
    rs = avg_gain / avg_loss
    result['rsi'] = 100 - (100 / (1 + rs))
    
    return result 