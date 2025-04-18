"""
移動平均線交叉策略模組

基於短期與長期移動平均線的交叉來產生交易信號
使用經典的 MA Cross 策略，當短期線上穿長期線時買入，下穿時賣出
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union

from .strategy_base import StrategyBase
from .moving_average import detect_sma_cross, calculate_sma
from ..trading.simulator import TradingSimulator


class MACrossStrategy(StrategyBase):
    """
    移動平均線交叉策略
    
    使用短期與長期移動平均線的交叉來產生交易信號：
    - 短期線上穿長期線 = 買入信號（黃金交叉）
    - 短期線下穿長期線 = 賣出信號（死亡交叉）
    
    Attributes
    ----------
    short_period : int
        短期移動平均線週期
    long_period : int
        長期移動平均線週期
    ma_type : str
        移動平均線類型，'sma' 或 'ema'
    """
    
    def __init__(
        self,
        short_period: int = 10,
        long_period: int = 50,
        ma_type: str = 'sma',
        name: str = "MA交叉策略"
    ):
        """
        初始化移動平均線交叉策略
        
        Parameters
        ----------
        short_period : int, default 10
            短期移動平均線週期
        long_period : int, default 50
            長期移動平均線週期
        ma_type : str, default 'sma'
            移動平均線類型，'sma' 或 'ema'
        name : str, default "MA交叉策略"
            策略名稱
        """
        super().__init__(name=name)
        
        if short_period >= long_period:
            raise ValueError("短期週期必須小於長期週期")
            
        self.short_period = short_period
        self.long_period = long_period
        self.ma_type = ma_type.lower()
        
        if self.ma_type not in ['sma', 'ema']:
            raise ValueError("移動平均線類型必須是 'sma' 或 'ema'")
        
        # 為策略名添加週期信息
        self.name = f"{name} ({short_period}/{long_period})"
        
        # 儲存交易模擬結果
        self.trade_simulator_result = None
            
    def prepare_data(self, data: pd.DataFrame, column: str = 'close') -> pd.DataFrame:
        """
        準備策略所需的數據，計算移動平均線
        
        Parameters
        ----------
        data : pd.DataFrame
            原始價格數據
        column : str, default 'close'
            用於計算移動平均線的價格列名
            
        Returns
        -------
        pd.DataFrame
            添加了移動平均線的數據
        """
        df = data.copy()
        
        # 確保日期作為索引
        if 'date' in df.columns and df.index.name != 'date':
            df = df.set_index('date')
        
        # 計算短期與長期移動平均線
        if self.ma_type == 'sma':
            # 使用 calculate_sma 計算簡單移動平均線
            df = calculate_sma(df, period=self.short_period, column=column)
            df = calculate_sma(df, period=self.long_period, column=column)
        else:  # ema
            # 計算指數移動平均線
            short_col = f'ema_{self.short_period}'
            long_col = f'ema_{self.long_period}'
            df[short_col] = df[column].ewm(span=self.short_period, adjust=False).mean()
            df[long_col] = df[column].ewm(span=self.long_period, adjust=False).mean()
            
        return df
            
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號
        
        此方法實現了 StrategyBase 的抽象方法，根據移動平均線交叉產生買賣信號
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料，必須包含 open, high, low, close 列
            
        Returns
        -------
        pd.DataFrame
            包含交易信號的 DataFrame，添加了 'signal' 列：
            - 1: 買入信號
            - 0: 無信號/持有
            - -1: 賣出信號
        """
        # 確保資料有正確的列
        required_cols = ['open', 'high', 'low', 'close']
        for col in required_cols:
            if col not in data.columns:
                raise ValueError(f"資料必須包含 '{col}' 列")
                
        # 準備數據，計算移動平均線
        df = self.prepare_data(data)
        
        # 初始化信號列
        df['signal'] = 0
        
        if self.ma_type == 'sma':
            # 使用 detect_sma_cross 函數偵測交叉點
            cross_points = detect_sma_cross(
                df, 
                short_period=self.short_period, 
                long_period=self.long_period
            )
            
            # 根據交叉點生成信號
            for point in cross_points:
                date = point['date']
                # 將字符串日期轉換為與 DataFrame 索引相同的格式
                if isinstance(date, str):
                    date = pd.to_datetime(date)
                    
                if date in df.index:
                    if point['type'] == 'golden_cross':
                        df.loc[date, 'signal'] = 1  # 買入信號
                    elif point['type'] == 'death_cross':
                        df.loc[date, 'signal'] = -1  # 賣出信號
        else:
            # 直接計算 EMA 交叉
            short_col = f'ema_{self.short_period}'
            long_col = f'ema_{self.long_period}'
            
            # 計算當前和前一期的差值
            df['curr_diff'] = df[short_col] - df[long_col]
            df['prev_diff'] = df['curr_diff'].shift(1)
            
            # 黃金交叉：前一天短期線在長期線下方，今天短期線在長期線上方
            df.loc[(df['prev_diff'] < 0) & (df['curr_diff'] > 0), 'signal'] = 1
            
            # 死亡交叉：前一天短期線在長期線上方，今天短期線在長期線下方
            df.loc[(df['prev_diff'] > 0) & (df['curr_diff'] < 0), 'signal'] = -1
            
            # 移除臨時欄位
            df = df.drop(['curr_diff', 'prev_diff'], axis=1)
            
        # 填充 NaN 值
        df['signal'] = df['signal'].fillna(0)
            
        return df
    
    def generate_position(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        根據交易信號生成持倉狀態
        
        Parameters
        ----------
        data : pd.DataFrame
            包含交易信號的 DataFrame
            
        Returns
        -------
        pd.DataFrame
            添加了持倉狀態的 DataFrame
        """
        df = data.copy()
        
        # 初始化持倉列，1表示持有多頭，0表示不持有，-1表示持有空頭
        df['position'] = 0
        
        # 根據信號生成持倉狀態
        position = 0
        for i, row in df.iterrows():
            # 如果有買入信號且當前無倉位
            if row['signal'] == 1 and position <= 0:
                position = 1
            # 如果有賣出信號且當前有多頭倉位
            elif row['signal'] == -1 and position >= 0:
                position = -1
                
            df.loc[i, 'position'] = position
            
        return df
    
    def run_backtest(
        self, 
        data: pd.DataFrame, 
        initial_capital: float = 100000.0,
        commission: float = 0.0
    ) -> Dict[str, Any]:
        """
        執行回測並返回詳細結果
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料
        initial_capital : float, default 100000.0
            初始資本
        commission : float, default 0.0
            交易成本費率
            
        Returns
        -------
        Dict[str, Any]
            回測結果，包含以下鍵值：
            - signals: 交易信號 DataFrame
            - positions: 持倉狀態 DataFrame
            - performance: 績效指標字典
            - trading_simulation: 交易模擬結果（如果有）
        """
        # 使用重寫的 backtest 方法進行回測
        result = self.backtest(data, initial_capital, commission)
        
        # 準備返回結果
        backtest_result = {
            'signals': self.signals,
            'positions': result,
            'performance': self.performance
        }
        
        # 添加交易模擬結果（如果有）
        if self.trade_simulator_result:
            backtest_result['trading_simulation'] = {
                'trade_log': result['trade_log'] if 'trade_log' in result else [],
                'final_cash': self.trade_simulator_result['final_cash'],
                'final_positions': self.trade_simulator_result['final_positions'],
                'portfolio_value': self.trade_simulator_result['portfolio_value'],
                'total_trades': self.trade_simulator_result['total_trades'],
                'performance': self.trade_simulator_result['performance']
            }
            
        return backtest_result
    
    def backtest(self, 
               data: pd.DataFrame, 
               initial_capital: float = 100000.0,
               commission: float = 0.0) -> pd.DataFrame:
        """
        執行策略回測並使用 TradingSimulator 進行交易模擬
        
        此方法重寫了 StrategyBase 的 backtest 方法，
        使用 TradingSimulator 進行更加真實的交易模擬
        
        Parameters
        ----------
        data : pd.DataFrame
            包含價格數據的 DataFrame，必須包含 date, open, high, low, close 等列
        initial_capital : float, default 100000.0
            初始資本
        commission : float, default 0.0
            交易成本費率，例如 0.003 表示 0.3% 交易費用
            
        Returns
        -------
        pd.DataFrame
            回測結果 DataFrame，包含以下列：
            - date: 日期
            - signal: 交易信號 (1=買入, 0=無, -1=賣出)
            - position: 持倉狀態 (1=持多, 0=無倉, -1=持空)
            - returns: 資產日回報率
            - strategy_returns: 策略日回報率
            - capital: 資本曲線
            - 其他交易模擬相關欄位
        """
        # 調用父類的 backtest 方法先獲取基本的回測結果
        self.signals = self.generate_signals(data)
        base_result = super().backtest(data, initial_capital, commission)
        
        # 把數值型信號 (-1, 0, 1) 轉換為 TradingSimulator 所需的字符串信號 ("SELL", "", "BUY")
        signal_df = self.signals.copy()
        signal_df['trade_signal'] = ""
        signal_df.loc[signal_df['signal'] == 1, 'trade_signal'] = "BUY"
        signal_df.loc[signal_df['signal'] == -1, 'trade_signal'] = "SELL"
        
        # 創建交易模擬器實例
        simulator = TradingSimulator(initial_cash=initial_capital)
        
        # 使用 simulate 方法執行交易模擬
        sim_result = simulator.simulate(
            df=signal_df,
            signal_column='trade_signal',
            symbol="HSI",
            quantity=1.0
        )
        
        # 將交易模擬結果添加到回測結果中
        base_result['trade_log'] = simulator.get_trade_log()
        base_result['final_cash'] = sim_result['final_cash']
        base_result['final_positions'] = sim_result['final_positions']
        base_result['portfolio_value'] = sim_result['portfolio_value']['total_value']
        base_result['total_trades'] = sim_result['total_trades']
        
        # 儲存模擬交易結果供後續分析使用
        self.trade_simulator_result = sim_result
        
        return base_result
        
    def summary(self) -> Dict[str, Any]:
        """
        返回策略摘要信息
        
        Returns
        -------
        Dict[str, Any]
            策略摘要，包含策略參數和績效指標
        """
        if not self.performance:
            return {
                'name': self.name,
                'short_period': self.short_period,
                'long_period': self.long_period,
                'ma_type': self.ma_type,
                'status': '未回測'
            }
        
        result = {
            'name': self.name,
            'short_period': self.short_period,
            'long_period': self.long_period,
            'ma_type': self.ma_type,
            'performance': self.performance
        }
        
        # 添加交易模擬結果（如果有）
        if self.trade_simulator_result:
            result['trading_simulation'] = {
                'final_cash': self.trade_simulator_result['final_cash'],
                'total_trades': self.trade_simulator_result['total_trades'],
                'portfolio_value': self.trade_simulator_result['portfolio_value'],
                'trade_performance': self.trade_simulator_result['performance']
            }
            
        return result 