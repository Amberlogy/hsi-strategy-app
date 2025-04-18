"""
Alpha Vantage 資料來源模組

提供從 Alpha Vantage API 獲取恆生指數及相關股票數據的功能
"""

import logging
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# 配置日誌
logger = logging.getLogger(__name__)

# 模擬的 Alpha Vantage API 基礎 URL
BASE_URL = "https://www.alphavantage.co/query"

# 從環境變數讀取 API 密鑰
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", "demo")


def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval: str = "daily",
    **kwargs
) -> Dict[str, Any]:
    """
    從 Alpha Vantage 獲取股票數據
    
    模擬從 Alpha Vantage API 獲取指定股票在指定日期範圍內的歷史數據
    
    Parameters
    ----------
    symbol : str
        股票代碼，例如 "HSI" 代表恆生指數
    start_date : str, optional
        開始日期，格式為 "YYYY-MM-DD"
    end_date : str, optional
        結束日期，格式為 "YYYY-MM-DD"
    interval : str, optional
        數據間隔，可選值為 "daily", "weekly", "monthly"，默認為 "daily"
    **kwargs
        其他可選參數
        
    Returns
    -------
    Dict[str, Any]
        包含股票數據的字典
    """
    logger.info(f"正在從 Alpha Vantage 獲取股票數據: {symbol}, 間隔: {interval}, 範圍: {start_date} 至 {end_date}")
    
    # 處理日期範圍
    if not start_date:
        start_date_obj = datetime.now() - timedelta(days=30)
    else:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        
    if not end_date:
        end_date_obj = datetime.now()
    else:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 驗證日期範圍
    if end_date_obj < start_date_obj:
        raise ValueError("結束日期不能早於開始日期")
    
    # 模擬 Alpha Vantage API 調用
    logger.info(f"模擬 API 調用: {BASE_URL}?function=TIME_SERIES_{interval.upper()}&symbol={symbol}&apikey={API_KEY}")
    
    # 根據不同間隔生成不同的數據點數量
    if interval == "daily":
        step_days = 1
    elif interval == "weekly":
        step_days = 7
    elif interval == "monthly":
        step_days = 30
    else:
        raise ValueError(f"不支援的間隔: {interval}")
    
    # 生成模擬數據
    data = _generate_mock_data(symbol, start_date_obj, end_date_obj, step_days)
    
    logger.info(f"成功獲取 {symbol} 的數據，共 {len(data['dates'])} 條記錄")
    return data


def get_exchange_rate(
    from_currency: str,
    to_currency: str = "USD",
    **kwargs
) -> Dict[str, Any]:
    """
    獲取匯率數據
    
    模擬從 Alpha Vantage 獲取指定貨幣對的匯率數據
    
    Parameters
    ----------
    from_currency : str
        原始貨幣代碼，例如 "HKD"
    to_currency : str, optional
        目標貨幣代碼，默認為 "USD"
    **kwargs
        其他可選參數
        
    Returns
    -------
    Dict[str, Any]
        包含匯率數據的字典
    """
    logger.info(f"正在從 Alpha Vantage 獲取匯率數據: {from_currency}/{to_currency}")
    
    # 模擬 API 調用
    logger.info(f"模擬 API 調用: {BASE_URL}?function=CURRENCY_EXCHANGE_RATE&from_currency={from_currency}&to_currency={to_currency}&apikey={API_KEY}")
    
    # 模擬匯率數據
    if from_currency == "HKD" and to_currency == "USD":
        exchange_rate = 0.127 + random.uniform(-0.005, 0.005)
    elif from_currency == "USD" and to_currency == "HKD":
        exchange_rate = 7.85 + random.uniform(-0.1, 0.1)
    else:
        # 對於其他貨幣對，生成隨機匯率
        exchange_rate = random.uniform(0.1, 10.0)
    
    # 模擬的響應數據
    response = {
        "Realtime Currency Exchange Rate": {
            "1. From_Currency Code": from_currency,
            "2. From_Currency Name": _get_currency_name(from_currency),
            "3. To_Currency Code": to_currency,
            "4. To_Currency Name": _get_currency_name(to_currency),
            "5. Exchange Rate": round(exchange_rate, 6),
            "6. Last Refreshed": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "7. Time Zone": "UTC"
        }
    }
    
    logger.info(f"成功獲取匯率數據: 1 {from_currency} = {round(exchange_rate, 6)} {to_currency}")
    return response


def _generate_mock_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    step_days: int
) -> Dict[str, Any]:
    """
    生成模擬股票數據
    
    Parameters
    ----------
    symbol : str
        股票代碼
    start_date : datetime
        開始日期
    end_date : datetime
        結束日期
    step_days : int
        日期間隔天數
        
    Returns
    -------
    Dict[str, Any]
        模擬的股票數據
    """
    # 計算日期範圍內的交易日
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 如果不是週末或使用週間隔
        if current_date.weekday() < 5 or step_days > 1:
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=step_days)
    
    # 根據不同股票代碼設置不同的基礎價格
    if symbol == "HSI":
        base_price = 18000
        volatility = 150
    elif symbol.startswith("^"):  # 指數
        base_price = 3500
        volatility = 50
    else:  # 個股
        base_price = random.uniform(50, 200)
        volatility = base_price * 0.02
    
    # 生成每日價格數據
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []
    volumes = []
    
    price = base_price
    for _ in dates:
        # 隨機生成價格變動
        change_pct = random.uniform(-1.2, 1.2)
        price_change = price * (change_pct / 100)
        price += price_change
        
        # 生成開高低收價格
        open_price = price - random.uniform(-volatility/2, volatility/2)
        close_price = price
        high_price = max(open_price, close_price) + random.uniform(0, volatility/2)
        low_price = min(open_price, close_price) - random.uniform(0, volatility/2)
        
        # 確保價格永遠為正
        open_price = max(open_price, 1)
        high_price = max(high_price, open_price)
        low_price = max(low_price, 1)
        low_price = min(low_price, open_price, close_price)
        close_price = max(close_price, 1)
        
        # 生成交易量
        volume = int(random.uniform(500000, 5000000))
        
        # 添加到數據列表
        open_prices.append(round(open_price, 2))
        high_prices.append(round(high_price, 2))
        low_prices.append(round(low_price, 2))
        close_prices.append(round(close_price, 2))
        volumes.append(volume)
    
    # 組合最終數據
    return {
        "symbol": symbol,
        "source": "Alpha Vantage",
        "dates": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volumes
    }


def _get_currency_name(currency_code: str) -> str:
    """
    根據貨幣代碼獲取貨幣名稱
    
    Parameters
    ----------
    currency_code : str
        貨幣代碼
        
    Returns
    -------
    str
        貨幣名稱
    """
    currency_names = {
        "USD": "United States Dollar",
        "HKD": "Hong Kong Dollar",
        "JPY": "Japanese Yen",
        "EUR": "Euro",
        "GBP": "British Pound Sterling",
        "AUD": "Australian Dollar",
        "CAD": "Canadian Dollar",
        "CHF": "Swiss Franc",
        "CNY": "Chinese Yuan"
    }
    
    return currency_names.get(currency_code, f"Unknown Currency ({currency_code})") 