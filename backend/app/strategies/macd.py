"""
MACD 策略模組

提供基於 MACD (Moving Average Convergence Divergence) 指標的交易策略
偵測 MACD 線與信號線的交叉，以及柱狀圖的變化
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union, Any

from .strategy_base import StrategyBase


def calculate_macd(
    df: pd.DataFrame, 
    fast_period: int = 12, 
    slow_period: int = 26, 
    signal_period: int = 9, 
    column: str = 'close'
) -> pd.DataFrame:
    """
    計算 MACD (Moving Average Convergence Divergence) 指標
    
    MACD 指標包含三個部分：
    - MACD 線：快速 EMA - 慢速 EMA
    - 信號線：MACD 線的 EMA
    - 柱狀圖：MACD 線 - 信號線
    
    Parameters
    ----------
    df : pd.DataFrame
        包含價格數據的 DataFrame
    fast_period : int, default 12
        快速 EMA 週期
    slow_period : int, default 26
        慢速 EMA 週期
    signal_period : int, default 9
        信號線 EMA 週期
    column : str, default 'close'
        用於計算的價格欄位名稱
        
    Returns
    -------
    pd.DataFrame
        原始 DataFrame 加上 MACD 相關欄位的副本：
        - macd_line: MACD 線
        - signal_line: 信號線
        - hist: 柱狀圖
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    if column not in df.columns:
        raise ValueError(f"DataFrame 中不存在 '{column}' 欄位")
        
    # 創建結果 DataFrame 的副本
    result = df.copy()
    
    # 計算快速和慢速 EMA
    fast_ema = result[column].ewm(span=fast_period, adjust=False).mean()
    slow_ema = result[column].ewm(span=slow_period, adjust=False).mean()
    
    # 計算 MACD 線
    result['macd_line'] = fast_ema - slow_ema
    
    # 計算信號線
    result['signal_line'] = result['macd_line'].ewm(span=signal_period, adjust=False).mean()
    
    # 計算柱狀圖
    result['hist'] = result['macd_line'] - result['signal_line']
    
    return result


def detect_macd_cross(
    df: pd.DataFrame,
    macd_col: str = 'macd_line',
    signal_col: str = 'signal_line'
) -> List[Dict[str, Any]]:
    """
    偵測 MACD 線與信號線的交叉點
    
    Parameters
    ----------
    df : pd.DataFrame
        包含 MACD 指標的 DataFrame，必須包含 macd_line 和 signal_line 欄位
    macd_col : str, default 'macd_line'
        MACD 線的欄位名稱
    signal_col : str, default 'signal_line'
        信號線的欄位名稱
        
    Returns
    -------
    List[Dict[str, Any]]
        交叉點列表，每個交叉點為一個字典，包含以下鍵：
        - date: 交叉發生的日期
        - type: 交叉類型 ('golden_cross' 或 'death_cross')
        - macd: MACD 線值
        - signal: 信號線值
        - hist: 柱狀圖值
    """
    # 檢查輸入數據
    if not isinstance(df, pd.DataFrame):
        raise TypeError("輸入必須是 pandas DataFrame")
    
    for col in [macd_col, signal_col]:
        if col not in df.columns:
            raise ValueError(f"DataFrame 中不存在 '{col}' 欄位")
            
    # 確保 DataFrame 有日期索引或日期欄位
    temp_df = df.copy()
    if 'date' in temp_df.columns and temp_df.index.name != 'date':
        temp_df = temp_df.set_index('date')
        has_date_column = True
    else:
        has_date_column = False
    
    # 計算 MACD 與信號線的差值
    temp_df['macd_diff'] = temp_df[macd_col] - temp_df[signal_col]
    
    # 偵測交叉點
    temp_df['prev_diff'] = temp_df['macd_diff'].shift(1)
    
    # 黃金交叉：MACD 線從下方穿越信號線
    golden_cross = (temp_df['prev_diff'] < 0) & (temp_df['macd_diff'] > 0)
    
    # 死亡交叉：MACD 線從上方穿越信號線
    death_cross = (temp_df['prev_diff'] > 0) & (temp_df['macd_diff'] < 0)
    
    # 找出所有交叉點
    cross_points = []
    
    for idx, row in temp_df[golden_cross | death_cross].iterrows():
        cross_type = 'golden_cross' if row['macd_diff'] > 0 else 'death_cross'
        
        # 準備交叉點數據
        cross_point = {
            'date': idx if not has_date_column else idx.strftime('%Y-%m-%d'),
            'type': cross_type,
            'macd': row[macd_col],
            'signal': row[signal_col],
            'hist': row['hist'] if 'hist' in row else row[macd_col] - row[signal_col]
        }
        
        cross_points.append(cross_point)
    
    return cross_points


class MACDStrategy(StrategyBase):
    """
    MACD 交叉策略
    
    基於 MACD 線與信號線的交叉來產生買賣信號：
    - MACD 線向上穿越信號線 = 買入信號（黃金交叉）
    - MACD 線向下穿越信號線 = 賣出信號（死亡交叉）
    
    MACD 計算：
    - MACD 線 = 快速 EMA - 慢速 EMA
    - 信號線 = MACD 線的 EMA
    - 柱狀圖 = MACD 線 - 信號線
    """
    
    def __init__(
        self, 
        fast_period: int = 12, 
        slow_period: int = 26,
        signal_period: int = 9,
        name: str = "MACD交叉策略"
    ):
        """
        初始化 MACD 策略
        
        Parameters
        ----------
        fast_period : int, default 12
            快速 EMA 週期
        slow_period : int, default 26
            慢速 EMA 週期
        signal_period : int, default 9
            信號線 EMA 週期
        name : str, default "MACD交叉策略"
            策略名稱
        """
        super().__init__(name=name)
        
        if fast_period >= slow_period:
            raise ValueError("快速週期必須小於慢速週期")
            
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
            
    def calculate_macd(self, data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        計算 MACD 指標
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料
        column : str, default 'close'
            用於計算 MACD 的列名
            
        Returns
        -------
        pd.DataFrame
            包含 MACD 指標的 DataFrame
        """
        df = data.copy()
        
        # 計算快速和慢速 EMA
        fast_ema = df[column].ewm(span=self.fast_period, adjust=False).mean()
        slow_ema = df[column].ewm(span=self.slow_period, adjust=False).mean()
        
        # 計算 MACD 線
        df['macd'] = fast_ema - slow_ema
        
        # 計算信號線
        df['macd_signal'] = df['macd'].ewm(span=self.signal_period, adjust=False).mean()
        
        # 計算柱狀圖
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        return df
    
    def detect_crossover(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        偵測 MACD 線與信號線交叉
        
        Parameters
        ----------
        data : pd.DataFrame
            包含 MACD 指標的 DataFrame
            
        Returns
        -------
        pd.DataFrame
            添加了交叉信號的 DataFrame
        """
        df = data.copy()
        
        # 計算前一天的差值
        df['prev_diff'] = df['macd'].shift(1) - df['macd_signal'].shift(1)
        # 計算當天的差值
        df['curr_diff'] = df['macd'] - df['macd_signal']
        
        # 黃金交叉：前一天 MACD 線在信號線下方，今天 MACD 線在信號線上方
        df['golden_cross'] = (df['prev_diff'] < 0) & (df['curr_diff'] > 0)
        
        # 死亡交叉：前一天 MACD 線在信號線上方，今天 MACD 線在信號線下方
        df['death_cross'] = (df['prev_diff'] > 0) & (df['curr_diff'] < 0)
        
        # 移除臨時欄位
        df = df.drop(['prev_diff', 'curr_diff'], axis=1)
        
        return df
    
    def detect_divergence(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        偵測 MACD 背離
        
        背離是指 MACD 指標與價格走勢不一致的現象：
        - 價格創新高，但 MACD 未跟隨創新高 = 頂部背離（看跌）
        - 價格創新低，但 MACD 未跟隨創新低 = 底部背離（看漲）
        
        Parameters
        ----------
        data : pd.DataFrame
            包含 MACD 指標的 DataFrame
            
        Returns
        -------
        pd.DataFrame
            添加了背離信號的 DataFrame
        """
        df = data.copy()
        lookback = 20  # 檢查過去 20 個交易日
        
        # 初始化背離列
        df['bullish_divergence'] = False
        df['bearish_divergence'] = False
        
        # 從有足夠歷史數據的點開始檢查
        for i in range(lookback, len(df)):
            # 提取過去 lookback 天的數據
            segment = df.iloc[i-lookback:i+1]
            
            # 檢查價格是否創新低
            if segment['close'].iloc[-1] < segment['close'].iloc[:-1].min():
                # 檢查 MACD 是否未創新低（底部背離-看漲）
                if segment['macd'].iloc[-1] > segment['macd'].iloc[:-1].min():
                    df.iloc[i, df.columns.get_loc('bullish_divergence')] = True
            
            # 檢查價格是否創新高
            if segment['close'].iloc[-1] > segment['close'].iloc[:-1].max():
                # 檢查 MACD 是否未創新高（頂部背離-看跌）
                if segment['macd'].iloc[-1] < segment['macd'].iloc[:-1].max():
                    df.iloc[i, df.columns.get_loc('bearish_divergence')] = True
                    
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
        
        # 計算 MACD 指標
        df = self.calculate_macd(df)
        
        # 偵測交叉
        df = self.detect_crossover(df)
        
        # 偵測背離（可選）
        # df = self.detect_divergence(df)
        
        # 生成信號（1=買入，0=持有，-1=賣出）
        df['signal'] = 0
        
        # 黃金交叉時買入
        df.loc[df['golden_cross'], 'signal'] = 1
        
        # 死亡交叉時賣出
        df.loc[df['death_cross'], 'signal'] = -1
        
        # 可以添加背離信號（可選）
        # df.loc[df['bullish_divergence'], 'signal'] = 1
        # df.loc[df['bearish_divergence'], 'signal'] = -1
        
        # 填充 NaN 值為 0
        df['signal'] = df['signal'].fillna(0)
        
        # 生成持倉信號（1=持有多頭，0=不持有，-1=持有空頭）
        df['position'] = df['signal'].replace(to_replace=0, method='ffill')
        df['position'] = df['position'].fillna(0)
        
        return df 