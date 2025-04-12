"""
交易紀錄儲存模組

提供交易紀錄的儲存和檢索功能，支援 Redis 和本地文件儲存
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import pandas as pd

# 導入 Redis 快取模組
from app.core.redis_cache import redis_client, get_cache, set_cache

logger = logging.getLogger(__name__)

# Redis 鍵格式
TRADE_LOG_KEY_TEMPLATE = "trade:log:{user_id}:{strategy_id}"

# 本地儲存設定
LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data", "trade_logs")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


def _generate_redis_key(user_id: str, strategy_id: str) -> str:
    """
    生成 Redis 鍵
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : str
        策略 ID
        
    Returns
    -------
    str
        Redis 鍵
    """
    return TRADE_LOG_KEY_TEMPLATE.format(user_id=user_id, strategy_id=strategy_id)


def _get_local_storage_path(user_id: str, strategy_id: str) -> str:
    """
    獲取本地儲存路徑
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : str
        策略 ID
        
    Returns
    -------
    str
        本地儲存路徑
    """
    filename = f"{user_id}_{strategy_id}.json"
    return os.path.join(LOCAL_STORAGE_DIR, filename)


def save_trade_log(user_id: str, strategy_id: str, log_data: Dict[str, Any], expire_seconds: int = 86400 * 30) -> bool:
    """
    儲存交易紀錄
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : str
        策略 ID
    log_data : Dict[str, Any]
        交易紀錄數據，通常包含：
        - trade_log: 交易詳情列表
        - final_cash: 最終資金
        - final_positions: 最終持倉
        - portfolio_value: 投資組合價值
        - performance: 績效摘要
    expire_seconds : int, optional
        Redis 快取過期時間（秒），默認 30 天
        
    Returns
    -------
    bool
        是否成功儲存
    """
    # 添加時間戳
    if "timestamp" not in log_data:
        log_data["timestamp"] = datetime.now().isoformat()
    
    # 生成 Redis 鍵
    redis_key = _generate_redis_key(user_id, strategy_id)
    
    # 嘗試儲存到 Redis
    success = False
    if redis_client is not None:
        try:
            # 序列化並儲存
            success = set_cache(redis_key, log_data, expire_seconds)
            if success:
                logger.info(f"成功將交易紀錄儲存到 Redis: {redis_key}")
        except Exception as e:
            logger.error(f"向 Redis 儲存交易紀錄時出錯: {str(e)}")
    
    # 如果 Redis 儲存失敗或不可用，嘗試本地儲存
    if not success:
        try:
            local_path = _get_local_storage_path(user_id, strategy_id)
            
            # 讀取現有記錄（如果有）
            existing_data = []
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                    if not isinstance(existing_data, list):
                        existing_data = [existing_data]
            
            # 添加新記錄
            existing_data.append(log_data)
            
            # 寫入文件
            with open(local_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"成功將交易紀錄儲存到本地文件: {local_path}")
            success = True
        except Exception as e:
            logger.error(f"向本地文件儲存交易紀錄時出錯: {str(e)}")
    
    return success


def load_trade_log(user_id: str, strategy_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    讀取交易紀錄
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : str
        策略 ID
        
    Returns
    -------
    Optional[List[Dict[str, Any]]]
        交易紀錄列表，如果不存在或出錯則返回 None
    """
    # 生成 Redis 鍵
    redis_key = _generate_redis_key(user_id, strategy_id)
    
    # 嘗試從 Redis 讀取
    data = None
    if redis_client is not None:
        try:
            data = get_cache(redis_key)
            if data:
                logger.info(f"成功從 Redis 讀取交易紀錄: {redis_key}")
                # 確保返回的是列表
                if not isinstance(data, list):
                    data = [data]
        except Exception as e:
            logger.error(f"從 Redis 讀取交易紀錄時出錯: {str(e)}")
    
    # 如果 Redis 讀取失敗或不可用，嘗試從本地讀取
    if data is None:
        try:
            local_path = _get_local_storage_path(user_id, strategy_id)
            if os.path.exists(local_path):
                with open(local_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 確保返回的是列表
                    if not isinstance(data, list):
                        data = [data]
                logger.info(f"成功從本地文件讀取交易紀錄: {local_path}")
        except Exception as e:
            logger.error(f"從本地文件讀取交易紀錄時出錯: {str(e)}")
    
    return data


def get_latest_trade_log(user_id: str, strategy_id: str) -> Optional[Dict[str, Any]]:
    """
    獲取最近的交易紀錄
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : str
        策略 ID
        
    Returns
    -------
    Optional[Dict[str, Any]]
        最近的交易紀錄，如果不存在或出錯則返回 None
    """
    logs = load_trade_log(user_id, strategy_id)
    if not logs:
        return None
    
    # 按時間戳排序，返回最新的
    logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    return logs[0]


def clear_trade_logs(user_id: str, strategy_id: Optional[str] = None) -> bool:
    """
    清除交易紀錄
    
    Parameters
    ----------
    user_id : str
        用戶 ID
    strategy_id : Optional[str], optional
        策略 ID，如果為 None，則清除該用戶的所有策略紀錄
        
    Returns
    -------
    bool
        是否成功清除
    """
    success = False
    
    # 清除 Redis 中的記錄
    if redis_client is not None:
        try:
            if strategy_id:
                redis_key = _generate_redis_key(user_id, strategy_id)
                success = bool(set_cache(redis_key, None, 1))  # 設置為 None 並立即過期
            else:
                pattern = f"trade:log:{user_id}:*"
                from app.core.redis_cache import clear_cache_by_pattern
                success = bool(clear_cache_by_pattern(pattern))
        except Exception as e:
            logger.error(f"清除 Redis 交易紀錄時出錯: {str(e)}")
    
    # 清除本地文件中的記錄
    try:
        if strategy_id:
            local_path = _get_local_storage_path(user_id, strategy_id)
            if os.path.exists(local_path):
                os.remove(local_path)
                success = True
        else:
            for filename in os.listdir(LOCAL_STORAGE_DIR):
                if filename.startswith(f"{user_id}_") and filename.endswith(".json"):
                    os.remove(os.path.join(LOCAL_STORAGE_DIR, filename))
                    success = True
    except Exception as e:
        logger.error(f"清除本地文件交易紀錄時出錯: {str(e)}")
    
    return success


def to_dataframe(trade_logs: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    將交易紀錄轉換為 DataFrame
    
    Parameters
    ----------
    trade_logs : List[Dict[str, Any]]
        交易紀錄列表
        
    Returns
    -------
    pd.DataFrame
        交易紀錄 DataFrame
    """
    # 展平交易日誌
    flattened_logs = []
    for log in trade_logs:
        if 'trade_log' in log:
            for trade in log['trade_log']:
                # 添加策略績效信息
                if 'performance' in log:
                    trade.update(log['performance'])
                # 添加時間戳
                if 'timestamp' in log:
                    trade['log_timestamp'] = log['timestamp']
                flattened_logs.append(trade)
    
    if not flattened_logs:
        return pd.DataFrame()
        
    return pd.DataFrame(flattened_logs) 