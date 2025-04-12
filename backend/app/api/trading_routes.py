"""
交易紀錄 API 路由模組

提供保存和載入交易紀錄的 API 接口
"""

from fastapi import APIRouter, Query, HTTPException, Body, Depends
from typing import Optional, List, Dict, Any
import logging
import json
import os
import pandas as pd
import numpy as np
from datetime import datetime
from pydantic import BaseModel, Field

from app.strategies.statistics import evaluate_strategy

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(tags=["交易"])

# 交易紀錄資料夾路徑
TRADE_LOGS_DIR = "data/trade_logs"

# 確保交易紀錄資料夾存在
os.makedirs(TRADE_LOGS_DIR, exist_ok=True)

# 交易紀錄模型
class TradeRecord(BaseModel):
    user_id: str = Field(..., description="使用者 ID")
    strategy_id: str = Field(..., description="策略 ID")
    symbol: str = Field(..., description="交易標的")
    trade_type: str = Field(..., description="交易類型 (buy/sell)")
    quantity: float = Field(..., description="交易數量")
    price: float = Field(..., description="交易價格")
    timestamp: str = Field(..., description="交易時間 (ISO 格式)")
    note: Optional[str] = Field(None, description="交易備註")
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user123",
                "strategy_id": "ma_cross_1",
                "symbol": "HSI",
                "trade_type": "buy",
                "quantity": 1.0,
                "price": 18532.5,
                "timestamp": "2023-05-15T09:30:00",
                "note": "MA 交叉買入信號"
            }
        }

@router.post("/log/save", response_model=Dict[str, Any])
async def save_trade_log(trade: TradeRecord = Body(...)):
    """
    儲存一筆交易紀錄
    
    接收包含交易詳情的 JSON 物件，將其儲存為檔案
    
    Parameters
    ----------
    trade : TradeRecord
        包含交易詳情的物件
        
    Returns
    -------
    Dict[str, Any]
        儲存結果狀態
    """
    try:
        # 生成檔案名，格式為 user_id_strategy_id_timestamp.json
        timestamp = datetime.fromisoformat(trade.timestamp).strftime("%Y%m%d%H%M%S")
        filename = f"{trade.user_id}_{trade.strategy_id}_{timestamp}.json"
        file_path = os.path.join(TRADE_LOGS_DIR, filename)
        
        # 將交易紀錄轉換為 JSON 並寫入檔案
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(trade.json(indent=2))
            
        logger.info(f"已儲存交易紀錄: {filename}")
        
        # 回傳儲存成功的訊息和檔案名稱
        return {
            "status": "success",
            "message": "交易紀錄已成功儲存",
            "filename": filename
        }
        
    except Exception as e:
        logger.error(f"儲存交易紀錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"儲存交易紀錄時發生錯誤: {str(e)}"
        )

@router.get("/log/load", response_model=List[TradeRecord])
async def load_trade_logs(
    user_id: str = Query(..., description="使用者 ID"),
    strategy_id: Optional[str] = Query(None, description="策略 ID (可選)")
):
    """
    查詢交易紀錄
    
    根據使用者 ID 和可選的策略 ID 查詢交易紀錄
    
    Parameters
    ----------
    user_id : str
        使用者 ID
    strategy_id : str, optional
        策略 ID (可選)
        
    Returns
    -------
    List[TradeRecord]
        交易紀錄列表
    """
    try:
        # 檢查資料夾是否存在
        if not os.path.exists(TRADE_LOGS_DIR):
            return []
            
        # 取得所有符合條件的交易紀錄檔案
        records = []
        
        for filename in os.listdir(TRADE_LOGS_DIR):
            if not filename.endswith(".json"):
                continue
                
            # 檢查檔案名是否符合使用者 ID
            if not filename.startswith(f"{user_id}_"):
                continue
                
            # 如果指定了策略 ID，檢查檔案名是否符合
            if strategy_id and f"_{strategy_id}_" not in filename:
                continue
                
            # 讀取交易紀錄檔案
            file_path = os.path.join(TRADE_LOGS_DIR, filename)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    trade_data = json.load(f)
                    records.append(TradeRecord(**trade_data))
            except Exception as e:
                logger.warning(f"讀取交易紀錄 {filename} 時發生錯誤: {str(e)}")
                continue
                
        # 根據時間戳排序交易紀錄
        records.sort(key=lambda x: x.timestamp)
        
        logger.info(f"已查詢到 {len(records)} 筆交易紀錄，使用者 ID: {user_id}" + 
                   (f", 策略 ID: {strategy_id}" if strategy_id else ""))
        
        return records
        
    except Exception as e:
        logger.error(f"查詢交易紀錄時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"查詢交易紀錄時發生錯誤: {str(e)}"
        )

@router.get("/summary", response_model=Dict[str, Any])
async def get_trade_summary(
    user_id: str = Query(..., description="使用者 ID"),
    strategy_id: str = Query(..., description="策略 ID")
):
    """
    取得交易績效摘要
    
    根據使用者 ID 和策略 ID 計算交易策略的績效統計資訊
    
    Parameters
    ----------
    user_id : str
        使用者 ID
    strategy_id : str
        策略 ID
        
    Returns
    -------
    Dict[str, Any]
        包含交易統計資訊的字典，包括總報酬、交易次數、勝率、最大虧損等
    """
    try:
        # 首先獲取該使用者和策略的所有交易紀錄
        records = await load_trade_logs(user_id=user_id, strategy_id=strategy_id)
        
        if not records:
            return {
                "status": "info",
                "message": "未找到交易紀錄",
                "total_return": 0.0,
                "annual_return": 0.0,
                "max_drawdown": 0.0,
                "trade_count": 0,
                "win_rate": 0.0,
                "sharpe_ratio": 0.0,
                "volatility": 0.0
            }
        
        # 將交易紀錄轉換為適合策略評估的資料結構
        # 首先將紀錄按時間排序
        records.sort(key=lambda x: x.timestamp)
        
        # 創建一個 DataFrame 用於儲存交易資料
        df = pd.DataFrame({
            'timestamp': [datetime.fromisoformat(r.timestamp) for r in records],
            'price': [r.price for r in records],
            'quantity': [r.quantity for r in records],
            'trade_type': [r.trade_type for r in records]
        })
        
        # 設定時間戳為索引
        df.set_index('timestamp', inplace=True)
        
        # 計算持倉變化
        df['position_change'] = df.apply(
            lambda row: row.quantity if row.trade_type == 'buy' else -row.quantity if row.trade_type == 'sell' else 0, 
            axis=1
        )
        
        # 計算累積持倉
        df['position'] = df['position_change'].cumsum()
        
        # 計算每筆交易的資金流
        df['cash_flow'] = -df['price'] * df['position_change']
        
        # 計算累積資金流
        df['cumulative_cash_flow'] = df['cash_flow'].cumsum()
        
        # 計算當前持倉市值
        df['market_value'] = df['position'] * df['price']
        
        # 計算總資產 = 現金 + 市值
        initial_capital = 100000  # 假設初始資本為 100,000
        df['capital'] = initial_capital + df['cumulative_cash_flow'] + df['market_value']
        
        # 計算每日回報率
        df['returns'] = df['price'].pct_change().fillna(0)
        
        # 計算策略回報率 (基於資本變化)
        df['strategy_returns'] = df['capital'].pct_change().fillna(0)
        
        # 使用 evaluate_strategy 函數評估績效
        performance = evaluate_strategy(df)
        
        # 格式化結果
        formatted_performance = {
            "status": "success",
            "message": f"已計算 {user_id} 使用者的 {strategy_id} 策略績效",
            "total_return": round(performance['total_return'] * 100, 2),  # 轉為百分比
            "annual_return": round(performance['annual_return'] * 100, 2),  # 轉為百分比
            "max_drawdown": round(performance['max_drawdown'] * 100, 2),  # 轉為百分比
            "trade_count": performance['trade_count'],
            "win_rate": round(performance['win_rate'] * 100, 2),  # 轉為百分比
            "sharpe_ratio": round(performance['sharpe_ratio'], 2),
            "volatility": round(performance['volatility'] * 100, 2)  # 轉為百分比
        }
        
        logger.info(f"已計算 {user_id} 使用者的 {strategy_id} 策略績效")
        return formatted_performance
        
    except Exception as e:
        logger.error(f"計算交易績效摘要時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"計算交易績效摘要時發生錯誤: {str(e)}"
        ) 