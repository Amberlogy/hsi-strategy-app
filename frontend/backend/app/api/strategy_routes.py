"""
策略相關 API 路由模組

提供策略回測相關的 API 接口
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import pandas as pd
import logging

from app.strategies import MACrossStrategy
from app.data.source_aastocks import get_hsi_history
# 導入用戶認證和策略綁定函數
from app.users.auth import get_current_user
from app.users.strategy_link import bind_strategy_to_user
from app.users.models import User

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(tags=["策略"])

# 支援的策略列表
SUPPORTED_STRATEGIES = {
    "macross": MACrossStrategy
}

@router.get("/backtest", response_model=Dict[str, Any])
async def backtest_strategy(
    symbol: str = Query(..., description="股票代碼，例如: HSI"),
    start_date: str = Query(..., description="開始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="結束日期 (YYYY-MM-DD)"),
    strategy_name: str = Query(..., description="策略名稱，目前支援: macross"),
    short_period: int = Query(5, description="短期移動平均線週期"),
    long_period: int = Query(20, description="長期移動平均線週期"),
    ma_type: str = Query("sma", description="移動平均線類型: sma 或 ema"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    執行策略回測
    
    根據指定的股票代碼、日期範圍和策略名稱，執行回測並回傳結果
    
    Parameters
    ----------
    symbol : str
        股票代碼
    start_date : str
        開始日期
    end_date : str
        結束日期
    strategy_name : str
        策略名稱
    short_period : int, default 5
        短期移動平均線週期
    long_period : int, default 20
        長期移動平均線週期
    ma_type : str, default "sma"
        移動平均線類型: sma 或 ema
    current_user : Optional[User]
        當前登入用戶（可選）
        
    Returns
    -------
    Dict[str, Any]
        回測結果，包含信號、持倉和績效指標
    """
    try:
        # 1. 驗證策略名稱
        strategy_name = strategy_name.lower()
        if strategy_name not in SUPPORTED_STRATEGIES:
            raise HTTPException(
                status_code=400, 
                detail=f"不支援的策略名稱: {strategy_name}。目前支援: {', '.join(SUPPORTED_STRATEGIES.keys())}"
            )
        
        # 2. 驗證日期格式
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="日期格式錯誤，請使用 YYYY-MM-DD 格式"
            )
            
        if end < start:
            raise HTTPException(
                status_code=400,
                detail="結束日期不能早於開始日期"
            )
        
        # 3. 獲取歷史數據
        logger.info(f"獲取 {symbol} 從 {start_date} 到 {end_date} 的歷史數據")
        
        try:
            price_data = get_hsi_history(symbol, start_date, end_date)
        except Exception as e:
            logger.error(f"獲取歷史數據錯誤: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"獲取歷史數據錯誤: {str(e)}"
            )
        
        if price_data.empty:
            raise HTTPException(
                status_code=404,
                detail=f"找不到 {symbol} 在指定日期範圍的數據"
            )
        
        # 4. 創建並配置策略
        logger.info(f"使用 {strategy_name} 策略，參數: short_period={short_period}, long_period={long_period}, ma_type={ma_type}")
        
        if strategy_name == "macross":
            strategy = MACrossStrategy(
                short_period=short_period,
                long_period=long_period,
                ma_type=ma_type
            )
        
        # 5. 執行回測
        logger.info("執行策略回測")
        try:
            result = strategy.run_backtest(price_data)
        except Exception as e:
            logger.error(f"回測執行錯誤: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"回測執行錯誤: {str(e)}"
            )
        
        # 6. 格式化回測結果
        # 將 DataFrame 轉換為 JSON 可序列化的格式
        signals_json = result["signals"].reset_index().to_dict(orient="records")
        positions_json = result["positions"].reset_index().to_dict(orient="records")
        
        # 格式化績效指標
        performance = result["performance"]
        formatted_performance = {
            "total_return": f"{performance['total_return']:.2%}",
            "annual_return": f"{performance['annual_return']:.2%}",
            "sharpe_ratio": f"{performance['sharpe_ratio']:.2f}",
            "max_drawdown": f"{performance['max_drawdown']:.2%}",
            "win_rate": f"{performance['win_rate']:.2%}",
            "trade_count": performance['trade_count']
        }
        
        # 7. 若用戶已登入，自動記錄策略至用戶綁定列表
        strategy_config = {
            "short_period": short_period,
            "long_period": long_period,
            "ma_type": ma_type,
            "symbol": symbol,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "performance": {
                "total_return": performance['total_return'],
                "annual_return": performance['annual_return'],
                "sharpe_ratio": performance['sharpe_ratio'],
                "max_drawdown": performance['max_drawdown'],
                "win_rate": performance['win_rate'],
                "trade_count": performance['trade_count']
            }
        }
        
        # 如果有登入用戶，綁定策略
        if current_user:
            logger.info(f"用戶 {current_user.username} (ID: {current_user.id}) 執行策略回測，將記錄至用戶策略列表")
            bind_result = bind_strategy_to_user(
                user_id=current_user.id, 
                strategy_id=strategy_name, 
                config=strategy_config
            )
            if not bind_result:
                logger.warning(f"無法將策略 {strategy_name} 綁定到用戶 {current_user.username}")
        
        # 8. 返回結果
        return {
            "strategy_name": strategy.name,
            "params": {
                "short_period": short_period,
                "long_period": long_period,
                "ma_type": ma_type
            },
            "symbol": symbol,
            "period": {
                "start_date": start_date,
                "end_date": end_date
            },
            "performance": formatted_performance,
            "signals": signals_json,
            "positions": positions_json
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"處理回測請求時發生錯誤: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"處理回測請求時發生錯誤: {str(e)}"
        ) 