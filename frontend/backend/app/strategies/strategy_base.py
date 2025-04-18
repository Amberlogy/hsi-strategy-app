"""
策略基底類別

為所有交易策略提供共同的基礎結構和方法
包括回測、評估和信號生成功能
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Any, Union

from .statistics import evaluate_strategy

# 可選導入 matplotlib，用於繪圖功能
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class StrategyBase(ABC):
    """
    策略基底抽象類別
    
    所有具體策略實現必須繼承此類別並實現必要方法。
    此基底類別提供交易策略的共同框架，包括回測與績效評估功能。
    
    Attributes
    ----------
    name : str
        策略名稱
    signals : pd.DataFrame
        信號數據，包含策略生成的交易信號
    positions : pd.DataFrame
        持倉數據，包含基於信號轉換的持倉狀態
    performance : Dict[str, Any]
        績效指標，包含回測結果的各項指標
    """
    
    def __init__(self, name: str = "BaseStrategy"):
        """
        初始化策略基底類別
        
        Parameters
        ----------
        name : str, default "BaseStrategy"
            策略名稱
        """
        self.name = name
        self.signals = pd.DataFrame()  # 信號資料
        self.positions = pd.DataFrame()  # 持倉資料
        self.performance = {}  # 績效指標
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信號
        
        此抽象方法必須由子類別實現，根據輸入資料生成交易信號
        
        Parameters
        ----------
        data : pd.DataFrame
            輸入的價格資料
            
        Returns
        -------
        pd.DataFrame
            包含交易信號的 DataFrame，必須包含 'signal' 欄位：
            - 1: 買入信號
            - 0: 無信號
            - -1: 賣出信號
        """
        pass
    
    def backtest(self, 
                data: pd.DataFrame, 
                initial_capital: float = 100000.0,
                commission: float = 0.0) -> pd.DataFrame:
        """
        執行策略回測
        
        基於歷史數據和策略生成的信號，模擬交易並計算績效
        
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
            - 其他策略特定列
            
        Examples
        --------
        >>> import pandas as pd
        >>> from app.strategies import MovingAverageStrategy
        >>> data = pd.DataFrame({
        ...     'date': pd.date_range(start='2023-01-01', periods=100),
        ...     'open': np.random.normal(100, 2, 100),
        ...     'high': np.random.normal(102, 2, 100),
        ...     'low': np.random.normal(98, 2, 100),
        ...     'close': np.random.normal(101, 2, 100)
        ... })
        >>> strategy = MovingAverageStrategy(fast_window=5, slow_window=20)
        >>> result = strategy.backtest(data)
        >>> print(f"最終資本: {result['capital'].iloc[-1]:.2f}")
        """
        # 首先生成信號
        self.signals = self.generate_signals(data)
        
        # 確保信號資料有正確欄位
        if 'signal' not in self.signals.columns:
            raise ValueError("信號 DataFrame 必須包含 'signal' 欄位")
            
        # 建立持倉資料框架
        self.positions = self.signals.copy()
        # 計算持倉變化 (正值表示增加持倉，負值表示減少持倉)
        self.positions['position'] = self.positions['signal'].diff()
        
        # 計算每日收益
        self.positions['returns'] = data['close'].pct_change()
        
        # 計算策略收益 (持倉狀態 * 收益率)
        self.positions['strategy_returns'] = self.positions['signal'].shift(1) * self.positions['returns']
        
        # 計算資本曲線
        self.positions['capital'] = initial_capital * (1 + self.positions['strategy_returns']).cumprod()
        
        # 應用交易成本
        if commission > 0:
            # 計算交易次數（position 有變化的天數）
            trades = self.positions[self.positions['position'] != 0].copy()
            total_commission = len(trades) * commission
            
            # 從最終資本中扣除總交易成本
            final_capital = self.positions['capital'].iloc[-1] * (1 - total_commission)
            self.positions.loc[self.positions.index[-1], 'capital'] = final_capital
        
        # 計算績效指標
        self.performance = self._calculate_performance()
        
        return self.positions
    
    def evaluate(self, result: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        評估策略績效
        
        計算並返回各種績效指標，如夏普比率，最大回撤等
        
        Parameters
        ----------
        result : pd.DataFrame, optional
            回測結果資料，如果提供則使用該資料進行評估，
            否則使用最近一次回測的結果 (self.positions)
            
        Returns
        -------
        Dict[str, Any]
            績效評估結果，包含以下鍵值：
            - total_return: 總回報率
            - annual_return: 年化收益率
            - annual_volatility: 年化波動率
            - sharpe_ratio: 夏普比率
            - max_drawdown: 最大回撤
            - win_rate: 勝率
            - trade_count: 交易次數
            
        Examples
        --------
        >>> import pandas as pd
        >>> from app.strategies import MovingAverageStrategy
        >>> data = pd.DataFrame({
        ...     'date': pd.date_range(start='2023-01-01', periods=100),
        ...     'open': np.random.normal(100, 2, 100),
        ...     'high': np.random.normal(102, 2, 100),
        ...     'low': np.random.normal(98, 2, 100),
        ...     'close': np.random.normal(101, 2, 100)
        ... })
        >>> strategy = MovingAverageStrategy(fast_window=5, slow_window=20)
        >>> strategy.backtest(data)
        >>> performance = strategy.evaluate()
        >>> print(f"年化收益率: {performance['annual_return']:.2%}")
        >>> print(f"夏普比率: {performance['sharpe_ratio']:.2f}")
        >>> print(f"最大回撤: {performance['max_drawdown']:.2%}")
        """
        # 如果提供了特定的回測結果，則使用該結果進行評估
        positions = result if result is not None else self.positions
        
        if positions.empty:
            raise ValueError("必須先執行 backtest() 方法才能評估績效")
            
        # 如果提供的回測結果與儲存的不同，則重新計算績效指標
        if result is not None:
            performance = self._calculate_performance(positions)
        else:
            performance = self.performance
            
        return performance
    
    def _calculate_performance(self, positions: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """
        計算策略績效指標
        
        內部方法，計算各種績效指標
        
        Parameters
        ----------
        positions : pd.DataFrame, optional
            持倉數據，如果未提供則使用 self.positions
            
        Returns
        -------
        Dict[str, Any]
            績效指標字典
        """
        if positions is None:
            positions = self.positions
            
        if positions.empty:
            return {}
            
        # 使用 statistics 模組中的 evaluate_strategy 函數計算績效指標
        return evaluate_strategy(positions)
        
    def plot_performance(self, 
                        result: Optional[pd.DataFrame] = None, 
                        benchmark: Optional[pd.DataFrame] = None) -> None:
        """
        繪製策略績效圖表
        
        Parameters
        ----------
        result : pd.DataFrame, optional
            回測結果資料，如果未提供則使用 self.positions
        benchmark : pd.DataFrame, optional
            基準資料，用於比較策略與市場表現
            
        Returns
        -------
        None
            顯示圖表
            
        Notes
        -----
        此方法需要 matplotlib.pyplot，使用前請確保已安裝相關套件：
        pip install matplotlib
        """
        if not MATPLOTLIB_AVAILABLE:
            print("繪製圖表需要 matplotlib 套件，請先安裝: pip install matplotlib")
            return
            
        positions = result if result is not None else self.positions
        
        if positions.empty:
            raise ValueError("必須先執行 backtest() 方法才能繪製績效圖表")
        
        fig, axes = plt.subplots(3, 1, figsize=(12, 14), gridspec_kw={'height_ratios': [2, 1, 1]})
        
        # 繪製資本曲線
        ax1 = axes[0]
        ax1.plot(positions.index, positions['capital'], 'b-', label=f'{self.name} 資本曲線')
        if benchmark is not None:
            # 假設基準數據也有資本曲線
            ax1.plot(benchmark.index, benchmark['capital'], 'r--', label='基準資本曲線')
        ax1.set_title('策略績效')
        ax1.set_ylabel('資本')
        ax1.legend()
        ax1.grid(True)
        
        # 繪製交易信號
        ax2 = axes[1]
        ax2.plot(positions.index, positions['close'], 'k-', alpha=0.3)
        # 買入信號
        buy_signals = positions[positions['signal'] == 1]
        ax2.scatter(buy_signals.index, buy_signals['close'], marker='^', color='g', s=100, label='買入信號')
        # 賣出信號
        sell_signals = positions[positions['signal'] == -1]
        ax2.scatter(sell_signals.index, sell_signals['close'], marker='v', color='r', s=100, label='賣出信號')
        ax2.set_title('交易信號')
        ax2.set_ylabel('價格')
        ax2.legend()
        ax2.grid(True)
        
        # 繪製回撤
        ax3 = axes[2]
        equity_curve = positions['capital'] / positions['capital'].iloc[0]
        running_max = equity_curve.cummax()
        drawdown = (running_max - equity_curve) / running_max
        ax3.fill_between(positions.index, 0, drawdown, color='r', alpha=0.3)
        ax3.set_title('回撤')
        ax3.set_ylabel('回撤幅度')
        ax3.set_xlabel('日期')
        ax3.grid(True)
        
        # 添加績效指標文字
        performance = self.evaluate(positions)
        textstr = '\n'.join([
            f"總回報: {performance['total_return']:.2%}",
            f"年化收益: {performance['annual_return']:.2%}",
            f"夏普比率: {performance['sharpe_ratio']:.2f}",
            f"最大回撤: {performance['max_drawdown']:.2%}",
            f"勝率: {performance['win_rate']:.2%}",
            f"交易次數: {performance['trade_count']}"
        ])
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
        fig.text(0.15, 0.95, textstr, fontsize=10, verticalalignment='top', bbox=props)
        
        plt.tight_layout()
        plt.show() 