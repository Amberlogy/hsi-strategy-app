from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import date, timedelta, datetime
import pandas as pd
import json
import logging
import os

# 配置日誌
logger = logging.getLogger(__name__)

# 導入 Redis 快取模組
from app.core import get_cache, set_cache
# 導入技術指標計算模組
from app.services.indicators import bollinger_bands
# 導入資料獲取模組
from app.data.source_aastocks import get_hsi_history
# 導入定時更新任務模組
from app.tasks.daily_update import get_latest_hsi_data

# 創建指標路由器
router = APIRouter()

@router.get("/macd", tags=["Indicators"])
async def get_macd(
    symbol: str = Query(..., description="股票代碼，例如：HSI"),
    period: int = Query(14, description="計算週期"),
    fast_period: int = Query(12, description="快線週期"),
    slow_period: int = Query(26, description="慢線週期"),
    signal_period: int = Query(9, description="信號線週期"),
) -> Dict:
    """
    計算 MACD (移動平均收斂發散) 指標
    
    返回:
        包含 MACD 線、信號線和柱狀圖數據的字典
    """
    try:
        # 這裡將來可以添加實際的計算邏輯
        # 目前返回模擬數據
        return {
            "symbol": symbol,
            "indicator": "MACD",
            "parameters": {
                "period": period,
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period
            },
            "values": {
                "macd_line": [0.42, 0.38, 0.36, 0.32, 0.28],
                "signal_line": [0.35, 0.36, 0.37, 0.36, 0.34],
                "histogram": [0.07, 0.02, -0.01, -0.04, -0.06]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算 MACD 指標時出錯: {str(e)}")

@router.get("/rsi", tags=["Indicators"])
async def get_rsi(
    symbol: str = Query(..., description="股票代碼，例如：HSI"),
    period: int = Query(14, description="計算週期"),
) -> Dict:
    """
    計算 RSI (相對強弱指數) 指標
    
    返回:
        包含 RSI 值的字典
    """
    try:
        # 這裡將來可以添加實際的計算邏輯
        # 目前返回模擬數據
        return {
            "symbol": symbol,
            "indicator": "RSI",
            "parameters": {
                "period": period
            },
            "values": [65.42, 63.38, 58.75, 54.32, 52.18]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算 RSI 指標時出錯: {str(e)}")

@router.get("/bollinger", tags=["Indicators"])
async def get_bollinger_bands(
    symbol: str = Query(..., description="股票代碼，例如：HSI"),
    start_date: date = Query(..., description="開始日期，格式：YYYY-MM-DD"),
    end_date: date = Query(..., description="結束日期，格式：YYYY-MM-DD"),
    period: int = Query(20, description="計算週期"),
    std_dev: float = Query(2.0, description="標準差倍數"),
) -> Dict:
    """
    計算布林帶指標
    
    返回:
        包含日期、SMA 和上下通道數據的字典
    """
    try:
        # 驗證日期範圍
        if start_date > end_date:
            raise HTTPException(status_code=400, detail="開始日期不能晚於結束日期")
            
        # 創建快取鍵，使用 symbol + 日期
        cache_key = f"bollinger:{symbol}:{start_date.isoformat()}:{end_date.isoformat()}:{period}:{std_dev}"
        
        # 嘗試從快取獲取數據
        cached_result = get_cache(cache_key)
        if cached_result:
            # 如果找到快取，記錄日誌並直接返回
            logger.info(f"從快取獲取布林帶數據: {cache_key}")
            return cached_result
        
        # 若沒有快取，記錄日誌並繼續計算
        logger.info(f"計算布林帶數據並設置快取: {cache_key}")
        
        # 使用 get_hsi_history 獲取實際數據
        df = get_hsi_history(
            symbol=symbol,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        # 確保日期列是 datetime 格式
        df['date'] = pd.to_datetime(df['date'])
        
        # 使用布林帶函數計算指標
        bb_result = bollinger_bands(df, period=period, std_dev=std_dev, column='close')
        
        # 整理結果為API響應格式
        result_data = []
        
        # 只處理不含 NaN 值的行
        valid_data = bb_result.dropna()
        
        for idx in valid_data.index:
            date_str = valid_data.loc[idx, 'date'].strftime('%Y-%m-%d')
            result_data.append({
                "date": date_str,
                "sma": round(valid_data.loc[idx, 'bb_middle'], 2),
                "upper_band": round(valid_data.loc[idx, 'bb_upper'], 2),
                "lower_band": round(valid_data.loc[idx, 'bb_lower'], 2),
                "width": round(valid_data.loc[idx, 'bb_width'], 4)
            })
            
        # 構建最終結果
        response_data = {
            "symbol": symbol,
            "indicator": "Bollinger Bands",
            "parameters": {
                "period": period,
                "std_dev": std_dev,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "data": result_data
        }
        
        # 設置快取，使用環境變數中定義的過期時間
        set_cache(cache_key, response_data)
            
        return response_data
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"計算布林帶指標時出錯: {str(e)}")
        raise HTTPException(status_code=500, detail=f"計算布林帶指標時出錯: {str(e)}")

@router.get("/hsi-history", tags=["Data"])
async def get_hsi_history_data(
    days: int = Query(7, description="要獲取的天數，默認為 7 天"),
) -> Dict:
    """
    獲取恆生指數的最近歷史數據
    
    從快取中獲取恆生指數的最近歷史數據，如果數據不存在，則自動更新
    
    Parameters
    ----------
    days : int, optional
        要獲取的天數，默認為 7 天
        
    Returns
    -------
    Dict
        包含恆生指數數據的字典
    """
    try:
        # 從快取中獲取數據
        history_data = get_latest_hsi_data(days)
        
        if not history_data:
            raise HTTPException(status_code=404, detail="無法獲取恆生指數歷史數據")
        
        # 整理數據為時間序列格式
        dates = []
        prices = {
            "open": [],
            "high": [],
            "low": [],
            "close": [],
            "volume": []
        }
        
        # 按日期排序
        sorted_dates = sorted(history_data.keys())
        
        for date_str in sorted_dates:
            daily_data = history_data[date_str]
            dates.append(date_str)
            prices["open"].append(daily_data["open"])
            prices["high"].append(daily_data["high"])
            prices["low"].append(daily_data["low"])
            prices["close"].append(daily_data["close"])
            prices["volume"].append(daily_data["volume"])
        
        return {
            "symbol": "HSI",
            "data_source": "cache",
            "dates": dates,
            "prices": prices
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        logger.error(f"獲取恆生指數歷史數據時出錯: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取恆生指數歷史數據時出錯: {str(e)}") 