"""
交易相關 API 路由模組

提供交易模擬和操作的 API 接口
"""

from fastapi import APIRouter, Query, HTTPException, Depends
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import logging

from app.trading.simulator import TradingSimulator
from app.data.source_aastocks import get_hsi_history
from app.strategies import MACrossStrategy
from app.strategies.moving_average import detect_sma_cross
# 導入用戶認證和策略綁定函數
from app.users.auth import get_current_user
from app.users.strategy_link import bind_strategy_to_user
from app.users.models import User

# 設置日誌
logger = logging.getLogger(__name__)

# 創建路由器
router = APIRouter(prefix="/api/trade", tags=["交易"])

# 全局交易模擬器實例
simulator = TradingSimulator(initial_cash=100000.0)

@router.get("/simulator/status", response_model=Dict[str, Any])
async def get_simulator_status():
    """
    獲取交易模擬器當前狀態
    
    Returns
    -------
    Dict[str, Any]
        模擬器狀態，包括：
        - cash: 當前資金
        - positions: 當前持倉
        - trade_log: 交易記錄
        - performance: 績效摘要
    """
    try:
        return {
            "cash": simulator.cash,
            "positions": simulator.get_positions(),
            "trade_log": simulator.get_trade_log(),
            "performance": simulator.get_performance_summary()
        }
    except Exception as e:
        logger.error(f"獲取模擬器狀態失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取模擬器狀態失敗: {str(e)}")

@router.post("/simulator/reset", response_model=Dict[str, Any])
async def reset_simulator(initial_cash: float = Query(100000.0, description="初始資金")):
    """
    重置交易模擬器
    
    Parameters
    ----------
    initial_cash : float, default 100000.0
        重置後的初始資金
        
    Returns
    -------
    Dict[str, Any]
        重置後的模擬器狀態
    """
    try:
        global simulator
        simulator = TradingSimulator(initial_cash=initial_cash)
        return {
            "message": "模擬器已重置",
            "cash": simulator.cash,
            "positions": simulator.get_positions(),
            "trade_log": simulator.get_trade_log()
        }
    except Exception as e:
        logger.error(f"重置模擬器失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"重置模擬器失敗: {str(e)}")

@router.post("/simulator/buy", response_model=Dict[str, Any])
async def buy_asset(
    symbol: str = Query(..., description="交易品種代碼，例如: HSI"),
    price: float = Query(..., description="買入價格"),
    quantity: float = Query(1.0, description="買入數量")
):
    """
    買入資產
    
    Parameters
    ----------
    symbol : str
        交易品種代碼
    price : float
        買入價格
    quantity : float, default 1.0
        買入數量
        
    Returns
    -------
    Dict[str, Any]
        交易詳情和更新後的模擬器狀態
    """
    try:
        trade = simulator.buy(symbol=symbol, price=price, quantity=quantity)
        return {
            "trade": trade,
            "cash": simulator.cash,
            "positions": simulator.get_positions(),
            "message": f"成功買入 {quantity} 單位 {symbol}，價格 {price}"
        }
    except ValueError as e:
        logger.error(f"買入操作失敗: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"買入操作失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"買入操作失敗: {str(e)}")

@router.post("/simulator/sell", response_model=Dict[str, Any])
async def sell_asset(
    symbol: str = Query(..., description="交易品種代碼，例如: HSI"),
    price: float = Query(..., description="賣出價格"),
    quantity: float = Query(1.0, description="賣出數量")
):
    """
    賣出資產
    
    Parameters
    ----------
    symbol : str
        交易品種代碼
    price : float
        賣出價格
    quantity : float, default 1.0
        賣出數量
        
    Returns
    -------
    Dict[str, Any]
        交易詳情和更新後的模擬器狀態
    """
    try:
        trade = simulator.sell(symbol=symbol, price=price, quantity=quantity)
        return {
            "trade": trade,
            "cash": simulator.cash,
            "positions": simulator.get_positions(),
            "message": f"成功賣出 {quantity} 單位 {symbol}，價格 {price}"
        }
    except (ValueError, KeyError) as e:
        logger.error(f"賣出操作失敗: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"賣出操作失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"賣出操作失敗: {str(e)}")

@router.post("/simulator/simulate", response_model=Dict[str, Any])
async def simulate_trading(
    start_date: str = Query(..., description="開始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="結束日期 (YYYY-MM-DD)"),
    strategy_name: str = Query("macross", description="策略名稱，目前支援: macross"),
    short_period: int = Query(5, description="短期移動平均線週期"),
    long_period: int = Query(20, description="長期移動平均線週期"),
    ma_type: str = Query("sma", description="移動平均線類型: sma 或 ema"),
    initial_cash: float = Query(100000.0, description="初始資金"),
    reset_simulator: bool = Query(True, description="是否重置模擬器"),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    使用指定策略進行交易模擬
    
    根據指定的策略、日期範圍和參數，執行交易模擬
    
    Parameters
    ----------
    start_date : str
        開始日期 (YYYY-MM-DD)
    end_date : str
        結束日期 (YYYY-MM-DD)
    strategy_name : str, default "macross"
        策略名稱，目前支援: macross
    short_period : int, default 5
        短期移動平均線週期
    long_period : int, default 20
        長期移動平均線週期
    ma_type : str, default "sma"
        移動平均線類型: sma 或 ema
    initial_cash : float, default 100000.0
        初始資金
    reset_simulator : bool, default True
        是否重置模擬器
    current_user : Optional[User]
        當前登入用戶（可選）
        
    Returns
    -------
    Dict[str, Any]
        模擬結果，包括：
        - trading_summary: 交易摘要
        - final_cash: 最終資金
        - final_positions: 最終持倉
        - trade_log: 交易記錄
        - performance: 績效指標
    """
    try:
        # 重置模擬器（如果需要）
        if reset_simulator:
            global simulator
            simulator = TradingSimulator(initial_cash=initial_cash)
        
        # 獲取歷史資料
        try:
            data = get_hsi_history(start_date, end_date)
        except Exception as e:
            logger.error(f"獲取歷史數據失敗: {str(e)}")
            raise HTTPException(status_code=500, detail=f"獲取歷史數據失敗: {str(e)}")
        
        # 根據策略類型執行不同邏輯
        if strategy_name.lower() == "macross":
            # 創建移動平均交叉策略實例
            strategy = MACrossStrategy(
                short_period=short_period,
                long_period=long_period,
                ma_type=ma_type
            )
            
            # 生成信號並轉換為交易模擬器所需的格式
            signals = strategy.generate_signals(data)
            signal_df = signals.copy()
            signal_df['trade_signal'] = ""
            signal_df.loc[signal_df['signal'] == 1, 'trade_signal'] = "BUY"
            signal_df.loc[signal_df['signal'] == -1, 'trade_signal'] = "SELL"
            
            # 使用模擬器執行交易模擬
            sim_result = simulator.simulate(
                df=signal_df,
                signal_column='trade_signal',
                symbol="HSI",
                quantity=1.0
            )
            
            # 添加策略特定的輸出
            sim_result['strategy'] = {
                'name': strategy_name,
                'short_period': short_period,
                'long_period': long_period,
                'ma_type': ma_type
            }
            
            # 若用戶已登入，自動記錄策略至用戶綁定列表
            if current_user:
                # 獲取績效數據
                performance_data = sim_result.get('performance', {})
                
                # 準備策略配置
                strategy_config = {
                    "short_period": short_period,
                    "long_period": long_period,
                    "ma_type": ma_type,
                    "symbol": "HSI",
                    "period": {
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    "initial_cash": initial_cash,
                    "performance": {
                        "total_return": performance_data.get('total_return', 0),
                        "win_rate": performance_data.get('win_rate', 0),
                        "trade_count": performance_data.get('trade_count', 0),
                        "profit_factor": performance_data.get('profit_factor', 0),
                        "max_drawdown": performance_data.get('max_drawdown', 0)
                    },
                    "simulator": True  # 標記此策略是通過模擬器執行的
                }
                
                logger.info(f"用戶 {current_user.username} (ID: {current_user.id}) 執行策略模擬，將記錄至用戶策略列表")
                bind_result = bind_strategy_to_user(
                    user_id=current_user.id, 
                    strategy_id=f"{strategy_name}_simulation", 
                    config=strategy_config
                )
                if not bind_result:
                    logger.warning(f"無法將策略 {strategy_name} 模擬結果綁定到用戶 {current_user.username}")
            
            return sim_result
        else:
            raise HTTPException(status_code=400, detail=f"不支援的策略: {strategy_name}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"執行交易模擬失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"執行交易模擬失敗: {str(e)}")

@router.get("/simulator/portfolio", response_model=Dict[str, Any])
async def get_portfolio_value(last_price: Optional[float] = None):
    """
    獲取當前投資組合價值
    
    Parameters
    ----------
    last_price : float, optional
        HSI 的最新價格，如果不提供則使用最近的收盤價
        
    Returns
    -------
    Dict[str, Any]
        投資組合價值詳情，包括：
        - total_value: 總價值
        - cash: 現金價值
        - positions_value: 持倉價值
        - positions_detail: 持倉詳情
    """
    try:
        # 如果未提供最新價格，嘗試獲取最近的收盤價
        if last_price is None:
            # 獲取最近一個交易日的數據
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            try:
                data = get_hsi_history(start_date, end_date)
                last_price = data['close'].iloc[-1]
            except Exception as e:
                logger.error(f"獲取最新價格失敗: {str(e)}")
                raise HTTPException(status_code=500, detail=f"無法獲取最新價格，請手動提供 last_price 參數")
        
        # 構建價格字典
        prices = {"HSI": last_price}
        
        # 獲取投資組合價值
        portfolio_value = simulator.get_portfolio_value(prices)
        
        return portfolio_value
    except Exception as e:
        logger.error(f"獲取投資組合價值失敗: {str(e)}")
        raise HTTPException(status_code=500, detail=f"獲取投資組合價值失敗: {str(e)}") 