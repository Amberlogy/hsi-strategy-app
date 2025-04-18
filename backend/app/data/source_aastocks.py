"""
AASTOCKS 資料來源模組

提供從 AASTOCKS 網站獲取恆生指數及相關股票數據的功能
"""

import logging
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any

# 配置日誌
logger = logging.getLogger(__name__)

# 模擬的資料獲取基礎 URL
BASE_URL = "https://www.aastocks.com/tc/stocks/quote/detail-quote.aspx"


def get_stock_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    從 AASTOCKS 獲取股票數據
    
    模擬從 AASTOCKS 網站獲取指定股票在指定日期範圍內的歷史數據
    
    Parameters
    ----------
    symbol : str
        股票代碼，例如 "HSI" 代表恆生指數
    start_date : str, optional
        開始日期，格式為 "YYYY-MM-DD"
    end_date : str, optional
        結束日期，格式為 "YYYY-MM-DD"
    **kwargs
        其他可選參數
        
    Returns
    -------
    Dict[str, Any]
        包含股票數據的字典
    """
    logger.info(f"正在從 AASTOCKS 獲取股票數據: {symbol}, 範圍: {start_date} 至 {end_date}")
    
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
    
    # 模擬生成股票數據
    data = _generate_mock_data(symbol, start_date_obj, end_date_obj)
    
    logger.info(f"成功獲取 {symbol} 的數據，共 {len(data['dates'])} 條記錄")
    return data


def get_hsi_history(
    symbol: str = "HSI",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> pd.DataFrame:
    """
    獲取恆生指數歷史數據並返回 DataFrame
    
    Parameters
    ----------
    symbol : str, optional
        股票或指數代碼，默認為 "HSI" (恆生指數)
    start_date : str, optional
        開始日期，格式為 "YYYY-MM-DD"
    end_date : str, optional
        結束日期，格式為 "YYYY-MM-DD"
        
    Returns
    -------
    pd.DataFrame
        包含歷史數據的 DataFrame，列包括 date, open, high, low, close, volume
    """
    logger.info(f"正在獲取 {symbol} 的歷史數據，範圍: {start_date} 至 {end_date}")
    
    # 處理日期範圍
    if not start_date:
        start_date_obj = datetime.now() - timedelta(days=90)  # 默認獲取過去90天的數據
    else:
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        
    if not end_date:
        end_date_obj = datetime.now()
    else:
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    # 驗證日期範圍
    if end_date_obj < start_date_obj:
        raise ValueError("結束日期不能早於開始日期")
    
    # 生成模擬數據 - 使用兩種方法之一
    use_sin_wave = random.choice([True, False])
    
    if use_sin_wave:
        # 使用 numpy sin 函數生成波動數據
        df = _generate_sin_wave_data(symbol, start_date_obj, end_date_obj)
    else:
        # 使用隨機波動生成數據
        data = _generate_mock_data(symbol, start_date_obj, end_date_obj)
        
        # 將字典轉換為 DataFrame
        df = pd.DataFrame({
            'date': data['dates'],
            'open': data['open'],
            'high': data['high'],
            'low': data['low'],
            'close': data['close'],
            'volume': data['volume']
        })
    
    # 設置日期為索引
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    logger.info(f"成功獲取 {symbol} 的歷史數據，共 {len(df)} 條記錄")
    return df


def get_index_constituents(symbol: str = "HSI") -> List[Dict[str, str]]:
    """
    獲取指數成分股
    
    模擬從 AASTOCKS 獲取指定指數的成分股列表
    
    Parameters
    ----------
    symbol : str
        指數代碼，默認為 "HSI" (恆生指數)
        
    Returns
    -------
    List[Dict[str, str]]
        成分股列表，每個成分股為一個字典，包含代碼和名稱
    """
    logger.info(f"正在從 AASTOCKS 獲取指數成分股: {symbol}")
    
    # 模擬恆生指數成分股
    constituents = [
        {"code": "00001", "name": "長和"},
        {"code": "00002", "name": "中電控股"},
        {"code": "00003", "name": "香港中華煤氣"},
        {"code": "00005", "name": "匯豐控股"},
        {"code": "00027", "name": "銀河娛樂"},
        {"code": "01299", "name": "友邦保險"},
        {"code": "00388", "name": "香港交易所"},
        {"code": "00700", "name": "騰訊控股"},
        {"code": "00941", "name": "中國移動"},
        {"code": "09988", "name": "阿里巴巴"}
    ]
    
    logger.info(f"成功獲取 {symbol} 的成分股，共 {len(constituents)} 支股票")
    return constituents


def _generate_sin_wave_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime
) -> pd.DataFrame:
    """
    使用 numpy sin 函數生成波動數據
    
    Parameters
    ----------
    symbol : str
        股票代碼
    start_date : datetime
        開始日期
    end_date : datetime
        結束日期
        
    Returns
    -------
    pd.DataFrame
        模擬的股票數據 DataFrame
    """
    # 計算日期範圍內的交易日（排除週末）
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 如果不是週末
        if current_date.weekday() < 5:
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    # 根據不同股票代碼設置不同的基礎價格
    if symbol == "HSI":
        base_price = 18000
        amplitude = 500
    else:
        # 為其他股票隨機生成基礎價格
        base_price = random.uniform(50, 500)
        amplitude = base_price * 0.1
    
    # 設置週期和相位
    period = random.uniform(20, 40)  # 週期天數
    phase_shift = random.uniform(0, 2 * np.pi)  # 隨機相位
    trend = random.uniform(-0.1, 0.1)  # 每日趨勢
    
    # 生成時間序列
    t = np.arange(len(dates))
    
    # 生成價格數據
    close_prices = base_price + amplitude * np.sin(2 * np.pi * t / period + phase_shift) + t * trend
    
    # 添加一些隨機波動
    noise = np.random.normal(0, amplitude * 0.05, len(dates))
    close_prices = close_prices + noise
    
    # 生成開高低收價格
    open_prices = close_prices + np.random.normal(0, amplitude * 0.02, len(dates))
    high_prices = np.maximum(close_prices, open_prices) + np.random.uniform(0, amplitude * 0.03, len(dates))
    low_prices = np.minimum(close_prices, open_prices) - np.random.uniform(0, amplitude * 0.03, len(dates))
    
    # 確保價格永遠為正
    open_prices = np.maximum(open_prices, 1)
    high_prices = np.maximum(high_prices, open_prices)
    low_prices = np.maximum(low_prices, 1)
    low_prices = np.minimum(low_prices, open_prices, close_prices)
    close_prices = np.maximum(close_prices, 1)
    
    # 生成交易量 - 使用相同的週期但有不同的相位
    volume_base = 5000000
    volume_amplitude = 3000000
    volume_phase = phase_shift + np.pi / 2  # 與價格錯開相位
    volumes = volume_base + volume_amplitude * np.sin(2 * np.pi * t / period + volume_phase) 
    volumes = volumes + np.random.normal(0, volume_amplitude * 0.1, len(dates))
    volumes = np.maximum(volumes, 100000)  # 確保交易量為正
    
    # 創建 DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': np.round(open_prices, 2),
        'high': np.round(high_prices, 2),
        'low': np.round(low_prices, 2),
        'close': np.round(close_prices, 2),
        'volume': volumes.astype(int)
    })
    
    return df


def _generate_mock_data(
    symbol: str,
    start_date: datetime,
    end_date: datetime
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
        
    Returns
    -------
    Dict[str, Any]
        模擬的股票數據
    """
    # 計算日期範圍內的交易日（假設週一至週五都是交易日）
    dates = []
    current_date = start_date
    while current_date <= end_date:
        # 如果不是週末
        if current_date.weekday() < 5:
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)
    
    # 根據不同股票代碼設置不同的基礎價格
    if symbol == "HSI":
        base_price = 18000
        volatility = 200
    else:
        # 為其他股票隨機生成基礎價格
        base_price = random.uniform(10, 500)
        volatility = base_price * 0.02
    
    # 生成每日價格數據
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []
    volumes = []
    
    price = base_price
    for _ in dates:
        # 隨機生成當天的價格變動
        change_pct = random.uniform(-1.5, 1.5)
        price_change = price * (change_pct / 100)
        price += price_change
        
        # 生成開高低收價格
        open_price = price - random.uniform(-volatility, volatility)
        close_price = price
        high_price = max(open_price, close_price) + random.uniform(0, volatility)
        low_price = min(open_price, close_price) - random.uniform(0, volatility)
        
        # 確保價格永遠為正
        open_price = max(open_price, 1)
        high_price = max(high_price, open_price)
        low_price = max(low_price, 1)
        low_price = min(low_price, open_price, close_price)
        close_price = max(close_price, 1)
        
        # 生成交易量
        volume = int(random.uniform(1000000, 10000000))
        
        # 添加到數據列表
        open_prices.append(round(open_price, 2))
        high_prices.append(round(high_price, 2))
        low_prices.append(round(low_price, 2))
        close_prices.append(round(close_price, 2))
        volumes.append(volume)
    
    # 組合最終數據
    return {
        "symbol": symbol,
        "source": "AASTOCKS",
        "dates": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volumes
    } 