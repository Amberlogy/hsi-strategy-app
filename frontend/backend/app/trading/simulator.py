"""
交易模擬器核心模組

提供模擬交易環境，追蹤資產、持倉和交易記錄
"""

import datetime
from typing import Dict, List, Any, Union
import pandas as pd


class TradingSimulator:
    """
    交易模擬器
    
    追蹤資金、持倉和交易記錄，支援買入和賣出操作
    
    Attributes
    ----------
    initial_cash : float
        初始資金
    cash : float
        當前資金
    positions : Dict[str, float]
        持倉列表，格式為 {symbol: quantity}
    trade_log : List[Dict[str, Any]]
        交易記錄列表
    """
    
    def __init__(self, initial_cash: float = 100000.0):
        """
        初始化交易模擬器
        
        Parameters
        ----------
        initial_cash : float, default 100000.0
            初始資金
        """
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.positions: Dict[str, float] = {}
        self.trade_log: List[Dict[str, Any]] = []
    
    def buy(self, symbol: str, price: float, quantity: float, timestamp=None) -> Dict[str, Any]:
        """
        買入操作
        
        Parameters
        ----------
        symbol : str
            交易品種代碼
        price : float
            買入價格
        quantity : float
            買入數量
        timestamp : Any, optional
            交易時間戳，默認為當前時間
            
        Returns
        -------
        Dict[str, Any]
            交易詳情
            
        Raises
        ------
        ValueError
            如果資金不足
        """
        # 計算交易成本
        cost = price * quantity
        
        # 檢查資金是否足夠
        if cost > self.cash:
            raise ValueError(f"資金不足: 需要 {cost}，當前資金 {self.cash}")
        
        # 執行交易
        self.cash -= cost
        
        # 更新持倉
        if symbol in self.positions:
            self.positions[symbol] += quantity
        else:
            self.positions[symbol] = quantity
        
        # 記錄交易
        timestamp = timestamp or datetime.datetime.now()
        trade = {
            "timestamp": timestamp,
            "symbol": symbol,
            "type": "buy",
            "price": price,
            "quantity": quantity,
            "cost": cost,
            "remaining_cash": self.cash
        }
        self.trade_log.append(trade)
        
        return trade
    
    def sell(self, symbol: str, price: float, quantity: float, timestamp=None) -> Dict[str, Any]:
        """
        賣出操作
        
        Parameters
        ----------
        symbol : str
            交易品種代碼
        price : float
            賣出價格
        quantity : float
            賣出數量
        timestamp : Any, optional
            交易時間戳，默認為當前時間
            
        Returns
        -------
        Dict[str, Any]
            交易詳情
            
        Raises
        ------
        ValueError
            如果持倉不足
        KeyError
            如果沒有該品種的持倉
        """
        # 檢查是否持有該品種
        if symbol not in self.positions:
            raise KeyError(f"沒有持有 {symbol}")
        
        # 檢查持倉是否足夠
        if self.positions[symbol] < quantity:
            raise ValueError(f"持倉不足: 需要 {quantity}，當前持倉 {self.positions[symbol]}")
        
        # 計算交易所得
        proceeds = price * quantity
        
        # 執行交易
        self.cash += proceeds
        self.positions[symbol] -= quantity
        
        # 如果持倉變為零，從持倉字典中移除
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        # 記錄交易
        timestamp = timestamp or datetime.datetime.now()
        trade = {
            "timestamp": timestamp,
            "symbol": symbol,
            "type": "sell",
            "price": price,
            "quantity": quantity,
            "proceeds": proceeds,
            "remaining_cash": self.cash
        }
        self.trade_log.append(trade)
        
        return trade
    
    def get_portfolio_value(self, current_prices: Dict[str, float]) -> Dict[str, float]:
        """
        計算投資組合總價值
        
        Parameters
        ----------
        current_prices : Dict[str, float]
            各個品種的當前價格，格式為 {symbol: price}
            
        Returns
        -------
        Dict[str, float]
            投資組合價值詳情，包括：
            - cash: 當前現金
            - positions_value: 持倉價值
            - total_value: 總價值
            - positions_detail: 各個持倉的價值
        """
        positions_value = 0.0
        positions_detail = {}
        
        # 計算持倉價值
        for symbol, quantity in self.positions.items():
            if symbol in current_prices:
                # 按當前價格計算持倉價值
                position_value = quantity * current_prices[symbol]
                positions_value += position_value
                positions_detail[symbol] = {
                    "quantity": quantity,
                    "current_price": current_prices[symbol],
                    "value": position_value
                }
            else:
                # 如果沒有提供當前價格，則標記為未知
                positions_detail[symbol] = {
                    "quantity": quantity,
                    "current_price": "unknown",
                    "value": "unknown"
                }
        
        # 計算總價值
        total_value = self.cash + positions_value
        
        return {
            "cash": self.cash,
            "positions_value": positions_value,
            "total_value": total_value,
            "positions_detail": positions_detail
        }
    
    def get_trade_log(self) -> List[Dict[str, Any]]:
        """
        獲取交易記錄
        
        Returns
        -------
        List[Dict[str, Any]]
            交易記錄列表
        """
        return self.trade_log
    
    def get_positions(self) -> Dict[str, float]:
        """
        獲取當前持倉
        
        Returns
        -------
        Dict[str, float]
            當前持倉，格式為 {symbol: quantity}
        """
        return self.positions.copy()
    
    def reset(self):
        """
        重置模擬器到初始狀態
        """
        self.cash = self.initial_cash
        self.positions = {}
        self.trade_log = []
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """
        獲取交易績效摘要
        
        Returns
        -------
        Dict[str, Any]
            績效摘要，包括：
            - total_trades: 總交易次數
            - buy_trades: 買入交易次數
            - sell_trades: 賣出交易次數
            - cash_change: 現金變化
            - cash_change_percent: 現金變化百分比
        """
        total_trades = len(self.trade_log)
        
        # 統計買入和賣出交易次數
        buy_trades = sum(1 for trade in self.trade_log if trade["type"] == "buy")
        sell_trades = sum(1 for trade in self.trade_log if trade["type"] == "sell")
        
        # 計算現金變化
        cash_change = self.cash - self.initial_cash
        cash_change_percent = (cash_change / self.initial_cash) * 100 if self.initial_cash != 0 else 0
        
        return {
            "total_trades": total_trades,
            "buy_trades": buy_trades,
            "sell_trades": sell_trades,
            "cash_change": cash_change,
            "cash_change_percent": cash_change_percent
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        將交易記錄轉換為 DataFrame
        
        Returns
        -------
        pd.DataFrame
            交易記錄 DataFrame
        """
        return pd.DataFrame(self.trade_log) 
        
    def simulate(self, df: pd.DataFrame, signal_column: str, symbol: str = "HSI", quantity: float = 1.0) -> Dict[str, Any]:
        """
        根據信號欄模擬交易過程
        
        Parameters
        ----------
        df : pd.DataFrame
            包含價格和信號的數據
        signal_column : str
            信號欄名稱，值為 "BUY" 或 "SELL"
        symbol : str, default "HSI"
            交易品種代碼
        quantity : float, default 1.0
            每次交易的數量
            
        Returns
        -------
        Dict[str, Any]
            模擬結果，包括：
            - final_cash: 最終資金
            - final_positions: 最終持倉
            - total_trades: 總交易次數
            - performance: 績效摘要
        """
        # 重置模擬器狀態
        self.reset()
        
        # 檢查信號欄是否存在
        if signal_column not in df.columns:
            raise ValueError(f"信號欄 '{signal_column}' 不存在")
        
        # 檢查價格欄是否存在
        if "close" not in df.columns and "price" not in df.columns:
            raise ValueError("缺少價格欄，需要 'close' 或 'price' 欄")
        
        # 確定價格欄
        price_column = "close" if "close" in df.columns else "price"
        
        # 遍歷 DataFrame 的每一行
        for index, row in df.iterrows():
            # 獲取當前價格和信號
            price = row[price_column]
            signal = row[signal_column]
            
            # 獲取日期/時間戳
            timestamp = index if isinstance(index, (datetime.datetime, datetime.date)) else row.get("date", index)
            
            # 根據信號執行交易
            try:
                if signal == "BUY":
                    # 嘗試買入
                    self.buy(symbol=symbol, price=price, quantity=quantity, timestamp=timestamp)
                elif signal == "SELL" and symbol in self.positions:
                    # 嘗試賣出，只有當持有該品種時才賣出
                    # 計算賣出數量，最多賣出全部持倉
                    sell_quantity = min(quantity, self.positions[symbol])
                    if sell_quantity > 0:
                        self.sell(symbol=symbol, price=price, quantity=sell_quantity, timestamp=timestamp)
            except (ValueError, KeyError):
                # 忽略交易錯誤（例如資金不足或持倉不足）
                # 但可以選擇記錄錯誤
                pass
        
        # 獲取當前持倉和最後價格
        final_positions = self.get_positions()
        last_prices = {symbol: df[price_column].iloc[-1]}
        
        # 計算最終投資組合價值
        portfolio_value = self.get_portfolio_value(last_prices)
        
        # 獲取績效摘要
        performance = self.get_performance_summary()
        
        # 返回模擬結果
        return {
            "final_cash": self.cash,
            "final_positions": final_positions,
            "portfolio_value": portfolio_value,
            "total_trades": len(self.trade_log),
            "performance": performance
        } 