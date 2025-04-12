"""
定時更新任務模組

包含每日更新恆生指數歷史數據的任務函數和排程設定
"""

import logging
import json
from datetime import datetime, timedelta
import pandas as pd

# 導入 APScheduler 相關模組
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

# 導入資料獲取模組
from app.data.source_aastocks import get_hsi_history
# 導入快取相關函數
from app.core import set_cache, get_cache, clear_cache_by_pattern
# 導入資料庫儲存模組
from app.data.storage import save_hsi_data, load_hsi_data

# 配置日誌
logger = logging.getLogger(__name__)

def update_hsi_data(use_db: bool = True, use_cache: bool = True) -> bool:
    """
    更新恆生指數歷史數據並寫入 Redis 快取和/或 SQLite 資料庫
    
    每日運行此函數獲取最新的恆生指數歷史數據，並將其存入 Redis 快取和/或 SQLite 資料庫
    
    Parameters
    ----------
    use_db : bool, optional
        是否將數據儲存到資料庫，默認為 True
    use_cache : bool, optional
        是否將數據儲存到 Redis 快取，默認為 True
        
    Returns
    -------
    bool
        更新是否成功
    """
    try:
        logger.info("開始更新恆生指數歷史數據")
        
        # 取得當前日期
        today = datetime.now()
        # 回溯 30 天以獲取最近一個月的數據
        start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        # 獲取恆生指數歷史數據
        df = get_hsi_history("HSI", start_date, end_date)
        
        if df.empty:
            logger.warning(f"獲取的恆生指數數據為空，日期範圍: {start_date} 至 {end_date}")
            return False
        
        # 確保日期列是 datetime 格式
        df['date'] = pd.to_datetime(df['date'])
        
        success = True
        
        # 儲存到 Redis 快取
        if use_cache:
            # 清除舊的數據快取 (可選)
            clear_result = clear_cache_by_pattern("hsi:*")
            logger.info(f"已清除 {clear_result} 個舊的快取項")
            
            # 將新數據寫入快取，按日期分別存儲
            cache_success_count = 0
            for _, row in df.iterrows():
                # 轉換日期為字符串格式作為快取鍵
                date_str = row['date'].strftime("%Y-%m-%d")
                cache_key = f"hsi:{date_str}"
                
                # 將當天數據轉為字典
                daily_data = {
                    "date": date_str,
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume'])
                }
                
                # 寫入快取，設置較長的過期時間 (例如 7 天)
                cache_success = set_cache(cache_key, daily_data, expire_seconds=604800)  # 7天 = 604800秒
                
                if cache_success:
                    cache_success_count += 1
            
            logger.info(f"恆生指數數據已更新到快取，成功寫入 {cache_success_count}/{len(df)} 天的數據")
            success = success and (cache_success_count > 0)
        
        # 儲存到 SQLite 資料庫
        if use_db:
            db_success = save_hsi_data(df)
            logger.info(f"恆生指數數據已{'成功' if db_success else '失敗'}更新到資料庫")
            success = success and db_success
        
        return success
        
    except Exception as e:
        logger.error(f"更新恆生指數數據時出錯: {str(e)}")
        return False

def get_latest_hsi_data(days: int = 7, use_db: bool = True, use_cache: bool = True) -> dict:
    """
    獲取最近幾天的恆生指數數據
    
    首先嘗試從 Redis 快取讀取，如果快取中沒有數據，則嘗試從資料庫讀取
    如果兩者都沒有數據，則重新更新數據
    
    Parameters
    ----------
    days : int, optional
        要獲取的天數，默認為 7 天
    use_db : bool, optional
        是否嘗試從資料庫讀取數據，默認為 True
    use_cache : bool, optional
        是否嘗試從 Redis 快取讀取數據，默認為 True
        
    Returns
    -------
    dict
        包含恆生指數數據的字典，格式為 {date: data}
    """
    result = {}
    today = datetime.now()
    
    # 如果啟用了快取，首先嘗試從快取中獲取數據
    if use_cache:
        # 嘗試從快取中獲取最近 days 天的數據
        for i in range(days):
            check_date = today - timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            cache_key = f"hsi:{date_str}"
            
            cached_data = get_cache(cache_key)
            if cached_data:
                result[date_str] = cached_data
        
        # 如果從快取中獲取到了足夠的數據，直接返回
        if len(result) >= days:
            return result
        
        logger.info(f"快取中的數據不完整，只找到 {len(result)}/{days} 天的數據")
    
    # 如果啟用了資料庫，嘗試從資料庫中獲取數據
    if use_db and (len(result) < days):
        start_date = (today - timedelta(days=days)).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
        
        logger.info(f"嘗試從資料庫獲取數據，日期範圍: {start_date} 至 {end_date}")
        db_df = load_hsi_data(start_date, end_date)
        
        if not db_df.empty:
            # 清空之前從快取獲取的數據
            result = {}
            
            # 將資料庫數據轉換為字典格式
            for _, row in db_df.iterrows():
                date_str = row['date'].strftime("%Y-%m-%d")
                result[date_str] = {
                    "date": date_str,
                    "open": float(row['open']),
                    "high": float(row['high']),
                    "low": float(row['low']),
                    "close": float(row['close']),
                    "volume": int(row['volume'])
                }
            
            logger.info(f"從資料庫獲取了 {len(result)} 天的數據")
            
            # 如果啟用了快取，將資料庫數據同步到快取
            if use_cache:
                logger.info("將資料庫數據同步到快取")
                for date_str, data in result.items():
                    cache_key = f"hsi:{date_str}"
                    set_cache(cache_key, data, expire_seconds=604800)
            
            return result
    
    # 如果數據仍然不完整，嘗試更新
    if len(result) < days:
        logger.info(f"數據不完整，只找到 {len(result)}/{days} 天的數據，嘗試更新")
        update_success = update_hsi_data(use_db=use_db, use_cache=use_cache)
        
        if update_success:
            # 重新執行一次獲取數據的過程
            return get_latest_hsi_data(days, use_db, use_cache)
    
    return result

def setup_scheduler():
    """
    設置 APScheduler 定時任務
    
    建立一個 BlockingScheduler 並設置每天早上 09:00 執行資料更新任務
    
    Returns
    -------
    BlockingScheduler
        設置好的排程器實例
    """
    logger.info("設置 APScheduler 定時任務")
    
    # 創建一個 BlockingScheduler
    scheduler = BlockingScheduler()
    
    # 添加每天早上 09:00 執行的任務
    scheduler.add_job(
        update_hsi_data,
        trigger=CronTrigger(hour=9, minute=0),  # 每天早上 9:00 執行
        id='update_hsi_data_job',
        name='每日更新恆生指數歷史數據',
        replace_existing=True
    )
    
    logger.info("APScheduler 任務已設置成功")
    return scheduler

if __name__ == "__main__":
    # 配置基本日誌
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 當直接運行此檔案時
    print("恆生指數數據更新任務排程器啟動...")
    
    # 更新一次數據，同時寫入快取和資料庫
    success = update_hsi_data(use_db=True, use_cache=True)
    print(f"初始數據更新{'成功' if success else '失敗'}")
    
    # 顯示最近幾天的數據
    latest_data = get_latest_hsi_data(3)  # 獲取最近 3 天的數據
    print(f"獲取到 {len(latest_data)} 天的數據:")
    for date, data in latest_data.items():
        print(f"日期: {date}, 收盤價: {data['close']}")
    
    # 啟動排程器
    scheduler = setup_scheduler()
    print(f"已設置排程任務: 每天早上 09:00 自動更新恆生指數數據")
    print("按 Ctrl+C 停止排程器")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("\n排程器已停止") 