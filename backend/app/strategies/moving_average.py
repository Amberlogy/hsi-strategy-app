"""
移動平均線策略模組

提供基於簡單移動平均線(SMA)和指數移動平均線(EMA)的交易策略
包括黃金交叉(Golden Cross)和死亡交叉(Death Cross)的判斷
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any

from .strategy_base import StrategyBase


def calculate_sma(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.DataFrame:
    """
    計算簡單移動平均線 (Simple Moving Average, SMA)
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame
    period : int, default 20
        移動平均線的週期
    column : str, default 'close'
        用於計算的價格欄位名稱
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上 SMA 欄位的副本
        新增欄位名稱格式為 'sma_{period}'，例如 'sma_20'
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'close': [100, 101, 102, 101, 99]})
    >>> result = calculate_sma(df, period=3)
    >>> print(result)
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 欄位")
        
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算 SMA
    sma_column = f'sma_{period}'
    result[sma_column] = result[column].rolling(window=period).mean()
    
    return result


def calculate_ema(df: pd.DataFrame, period: int = 20, column: str = 'close') -> pd.DataFrame:
    """
    計算指數移動平均線 (Exponential Moving Average, EMA)
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame
    period : int, default 20
        移動平均線的週期
    column : str, default 'close'
        用於計算的價格欄位名稱
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上 EMA 欄位的副本
        新增欄位名稱格式為 'ema_{period}'，例如 'ema_20'
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'close': [100, 101, 102, 101, 99]})
    >>> result = calculate_ema(df, period=3)
    >>> print(result)
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 欄位")
        
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算 EMA
    ema_column = f'ema_{period}'
    result[ema_column] = result[column].ewm(span=period, adjust=False).mean()
    
    return result


def detect_sma_cross(
    df: pd.DataFrame, 
    short_period: int = 10, 
    long_period: int = 50, 
    column: str = 'close'
) -> List[Dict[str, Any]]:
    """
    偵測短期與長期 SMA 的交叉點
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame
    short_period : int, default 10
        短期移動平均線週期
    long_period : int, default 50
        長期移動平均線週期
    column : str, default 'close'
        用於計算的價格欄位名稱
        
    Returns
    -------
    List[Dict[str, Any]]
        交叉點列表，每個交叉點為一個字典，包含以下鍵：
        - date: 交叉發生的日期
        - type: 交叉類型 ('golden_cross' 或 'death_cross')
        - short_ma: 短期移動平均線值
        - long_ma: 長期移動平均線值
        - price: 當日價格
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range(start='2023-01-01', periods=100),
    ...     'close': np.random.normal(100, 10, 100)
    ... })
    >>> result = detect_sma_cross(df)
    >>> print(f"發現 {len(result)} 個交叉點")
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 欄位")
        
    # 確保 DataFrame 有日期索引或日期欄位
    temp_df = df.copy()
    if 'date' in temp_df.columns and temp_df.index.name != 'date':
        temp_df = temp_df.set_index('date')
        has_date_column = True
    else:
        has_date_column = False
    
    # 計算短期和長期 SMA
    short_sma = temp_df[column].rolling(window=short_period).mean()
    long_sma = temp_df[column].rolling(window=long_period).mean()
    
    # 添加 SMA 欄位到 DataFrame
    temp_df[f'sma_{short_period}'] = short_sma
    temp_df[f'sma_{long_period}'] = long_sma
    
    # 計算 SMA 差值
    temp_df['sma_diff'] = temp_df[f'sma_{short_period}'] - temp_df[f'sma_{long_period}']
    
    # 偵測交叉點
    temp_df['prev_diff'] = temp_df['sma_diff'].shift(1)
    
    # 黃金交叉：短期 SMA 從下方穿越長期 SMA
    golden_cross = (temp_df['prev_diff'] < 0) & (temp_df['sma_diff'] > 0)
    
    # 死亡交叉：短期 SMA 從上方穿越長期 SMA
    death_cross = (temp_df['prev_diff'] > 0) & (temp_df['sma_diff'] < 0)
    
    # 找出所有交叉點
    cross_points = []
    
    for idx, row in temp_df[golden_cross | death_cross].iterrows():
        cross_type = 'golden_cross' if row['sma_diff'] > 0 else 'death_cross'
        
        # 準備交叉點數據
        cross_point = {
            'date': idx if not has_date_column else idx.strftime('%Y-%m-%d'),
            'type': cross_type,
            'short_ma': row[f'sma_{short_period}'],
            'long_ma': row[f'sma_{long_period}'],
            'price': row[column]
        }
        
        cross_points.append(cross_point)
    
    return cross_points


def detect_ema_cross(
    df: pd.DataFrame, 
    short_period: int = 10, 
    long_period: int = 50, 
    column: str = 'close'
) -> List[Dict[str, Any]]:
    """
    偵測短期與長期 EMA 的交叉點
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame
    short_period : int, default 10
        短期指數移動平均線週期
    long_period : int, default 50
        長期指數移動平均線週期
    column : str, default 'close'
        用於計算的價格欄位名稱
        
    Returns
    -------
    List[Dict[str, Any]]
        交叉點列表，每個交叉點為一個字典，包含以下鍵：
        - date: 交叉發生的日期
        - type: 交叉類型 ('golden_cross' 或 'death_cross')
        - short_ma: 短期移動平均線值
        - long_ma: 長期移動平均線值
        - price: 當日價格
    
    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({
    ...     'date': pd.date_range(start='2023-01-01', periods=100),
    ...     'close': np.random.normal(100, 10, 100)
    ... })
    >>> result = detect_ema_cross(df)
    >>> print(f"發現 {len(result)} 個交叉點")
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 欄位")
        
    # 確保 DataFrame 有日期索引或日期欄位
    temp_df = df.copy()
    if 'date' in temp_df.columns and temp_df.index.name != 'date':
        temp_df = temp_df.set_index('date')
        has_date_column = True
    else:
        has_date_column = False
    
    # 計算短期和長期 EMA
    short_ema = temp_df[column].ewm(span=short_period, adjust=False).mean()
    long_ema = temp_df[column].ewm(span=long_period, adjust=False).mean()
    
    # 添加 EMA 欄位到 DataFrame
    temp_df[f'ema_{short_period}'] = short_ema
    temp_df[f'ema_{long_period}'] = long_ema
    
    # 計算 EMA 差值
    temp_df['ema_diff'] = temp_df[f'ema_{short_period}'] - temp_df[f'ema_{long_period}']
    
    # 偵測交叉點
    temp_df['prev_diff'] = temp_df['ema_diff'].shift(1)
    
    # 黃金交叉：短期 EMA 從下方穿越長期 EMA
    golden_cross = (temp_df['prev_diff'] < 0) & (temp_df['ema_diff'] > 0)
    
    # 死亡交叉：短期 EMA 從上方穿越長期 EMA
    death_cross = (temp_df['prev_diff'] > 0) & (temp_df['ema_diff'] < 0)
    
    # 找出所有交叉點
    cross_points = []
    
    for idx, row in temp_df[golden_cross | death_cross].iterrows():
        cross_type = 'golden_cross' if row['ema_diff'] > 0 else 'death_cross'
        
        # 準備交叉點數據
        cross_point = {
            'date': idx if not has_date_column else idx.strftime('%Y-%m-%d'),
            'type': cross_type,
            'short_ma': row[f'ema_{short_period}'],
            'long_ma': row[f'ema_{long_period}'],
            'price': row[column]
        }
        
        cross_points.append(cross_point)
    
    return cross_points


class MovingAverageStrategy(StrategyBase):
    """
    移動平均線交叉策略
    
    基於快線與慢線的交叉來產生買賣信號：
    - 快線向上穿越慢線 = 買入信號（黃金交叉）
    - 快線向下穿越慢線 = 賣出信號（死亡交叉）
    """
    
    def __init__(
        self, 
        fast_window: int = 5, 
        slow_window: int = 20,
        ma_type: str = 'sma',
        name: str = "MA交叉策略"
    ):
        """
        初始化移動平均線策略
        
        Parameters
        ----------
        fast_window : int, default 5
            快線窗口大小
        slow_window : int, default 20
            慢線窗口大小
        ma_type : str, default 'sma'
            移動平均線類型，'sma' 或 'ema'
        name : str, default "MA交叉策略"
            策略名稱
        """
        super().__init__(name=name)
        
        if fast_window >= slow_window:
            raise ValueError("快線窗口必須小於慢線窗口")
            
        self.fast_window = fast_window
        self.slow_window = slow_window
        self.ma_type = ma_type.lower()
        
        if self.ma_type not in ['sma', 'ema']:
            raise ValueError("移動平均線類型必須是 'sma' 或 'ema'")
            
    def calculate_ma(self, data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        計算移動平均線
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料
        column : str, default 'close'
            用於計算移動平均線的列名
            
        Returns
        -------
        pd.DataFrame
            包含移動平均線的 DataFrame
        """
        df = data.copy()
        
        # 計算快線
        if self.ma_type == 'sma':
            df['fast_ma'] = df[column].rolling(window=self.fast_window).mean()
            df['slow_ma'] = df[column].rolling(window=self.slow_window).mean()
        else:  # ema
            df['fast_ma'] = df[column].ewm(span=self.fast_window, adjust=False).mean()
            df['slow_ma'] = df[column].ewm(span=self.slow_window, adjust=False).mean()
            
        return df
    
    def detect_crossover(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        偵測移動平均線交叉
        
        Parameters
        ----------
        data : pd.DataFrame
            包含移動平均線的 DataFrame
            
        Returns
        -------
        pd.DataFrame
            添加了交叉信號的 DataFrame
        """
        df = data.copy()
        
        # 計算前一天的差值
        df['prev_diff'] = df['fast_ma'].shift(1) - df['slow_ma'].shift(1)
        # 計算當天的差值
        df['curr_diff'] = df['fast_ma'] - df['slow_ma']
        
        # 黃金交叉：前一天快線在慢線下方，今天快線在慢線上方
        df['golden_cross'] = (df['prev_diff'] < 0) & (df['curr_diff'] > 0)
        
        # 死亡交叉：前一天快線在慢線上方，今天快線在慢線下方
        df['death_cross'] = (df['prev_diff'] > 0) & (df['curr_diff'] < 0)
        
        # 移除臨時欄位
        df = df.drop(['prev_diff', 'curr_diff'], axis=1)
        
        return df
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料
            
        Returns
        -------
        pd.DataFrame
            包含交易信號的 DataFrame
        """
        # 確保資料有正確的列
        required_cols = ['date', 'open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"資料必須包含 '{col}' 列")
                
        # 如果 'date' 不是索引，則設為索引
        df = data.copy()
        if 'date' in df.columns and df.index.name != 'date':
            df = df.set_index('date')
        
        # 計算移動平均線
        df = self.calculate_ma(df)
        
        # 偵測交叉
        df = self.detect_crossover(df)
        
        # 生成信號（1=買入，0=持有，-1=賣出）
        df['signal'] = 0
        
        # 黃金交叉時買入
        df.loc[df['golden_cross'], 'signal'] = 1
        
        # 死亡交叉時賣出
        df.loc[df['death_cross'], 'signal'] = -1
        
        # 填充 NaN 值為 0
        df['signal'] = df['signal'].fillna(0)
        
        # 生成持倉信號（1=持有多頭，0=不持有，-1=持有空頭）
        df['position'] = df['signal'].replace(to_replace=0, method='ffill')
        df['position'] = df['position'].fillna(0)
        
        return df 