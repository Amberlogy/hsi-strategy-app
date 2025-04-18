"""
Redis 快取模組

提供 Redis 連線和快取操作的功能
支援 JSON 序列化與反序列化
"""

import json
import logging
import os
from typing import Any, Optional, Union
from redis import Redis
from redis.exceptions import RedisError

# 加載環境變數
from dotenv import load_dotenv
load_dotenv()

# 配置日誌
logger = logging.getLogger(__name__)

# 從環境變數讀取 Redis 連線設定
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None) or None  # 處理空字串的情況
REDIS_PREFIX = "hsi:"  # 前綴以區分不同應用的快取

# 從環境變數讀取快取設定
DEFAULT_CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", 300))

# 環境設定
APP_ENV = os.getenv("APP_ENV", "development")

# 初始化 Redis 客戶端
try:
    redis_client = Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=False,  # 我們手動處理解碼，以支援二進制數據
        socket_timeout=5,
        socket_connect_timeout=5
    )
    # 嘗試連接
    redis_client.ping()
    logger.info(f"成功連接到 Redis 伺服器: {REDIS_HOST}:{REDIS_PORT}")
except RedisError as e:
    logger.warning(f"無法連接到 Redis 伺服器: {str(e)}，將使用模擬模式")
    redis_client = None
    
    # 在非開發環境下，Redis 連接失敗可能需要更嚴格處理
    if APP_ENV == "production":
        logger.error("生產環境下 Redis 連接失敗，這可能會導致性能問題！")


def _format_key(key: str) -> str:
    """
    格式化快取鍵名，添加前綴
    
    Parameters
    ----------
    key : str
        原始鍵名
        
    Returns
    -------
    str
        格式化後的鍵名
    """
    return f"{REDIS_PREFIX}{key}"


def get_cache(key: str) -> Optional[Any]:
    """
    從 Redis 獲取快取值
    
    支援 JSON 反序列化，如果值為 JSON 格式，將自動轉換為 Python 對象
    
    Parameters
    ----------
    key : str
        快取鍵名
        
    Returns
    -------
    Optional[Any]
        快取值，如果不存在或出錯則返回 None
    """
    if redis_client is None:
        logger.debug(f"Redis 處於模擬模式，無法獲取快取: {key}")
        return None
    
    formatted_key = _format_key(key)
    
    try:
        # 獲取二進制數據
        value = redis_client.get(formatted_key)
        
        if value is None:
            return None
        
        # 嘗試解析為 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, UnicodeDecodeError):
            # 如果不是 JSON，返回原始值
            return value
    except RedisError as e:
        logger.error(f"從 Redis 獲取快取時出錯: {str(e)}")
        return None


def set_cache(key: str, value: Any, expire_seconds: int = None) -> bool:
    """
    設置 Redis 快取值
    
    支援自動 JSON 序列化，能夠保存複雜的 Python 對象
    
    Parameters
    ----------
    key : str
        快取鍵名
    value : Any
        要快取的值，將自動序列化為 JSON
    expire_seconds : int, optional
        過期時間（秒），默認使用環境變數設定的值
        
    Returns
    -------
    bool
        是否成功設置快取
    """
    if redis_client is None:
        logger.debug(f"Redis 處於模擬模式，無法設置快取: {key}")
        return False
    
    # 如果未指定過期時間，使用環境變數中的默認值
    if expire_seconds is None:
        expire_seconds = DEFAULT_CACHE_TTL
    
    formatted_key = _format_key(key)
    
    try:
        # 序列化
        if isinstance(value, (dict, list, tuple, str, int, float, bool)) or value is None:
            value = json.dumps(value).encode('utf-8')
        
        # 設置值並設置過期時間
        return redis_client.setex(formatted_key, expire_seconds, value)
    except (RedisError, TypeError) as e:
        logger.error(f"向 Redis 設置快取時出錯: {str(e)}")
        return False


def delete_cache(key: str) -> bool:
    """
    從 Redis 刪除快取
    
    Parameters
    ----------
    key : str
        快取鍵名
        
    Returns
    -------
    bool
        是否成功刪除
    """
    if redis_client is None:
        logger.debug(f"Redis 處於模擬模式，無法刪除快取: {key}")
        return False
    
    formatted_key = _format_key(key)
    
    try:
        return bool(redis_client.delete(formatted_key))
    except RedisError as e:
        logger.error(f"從 Redis 刪除快取時出錯: {str(e)}")
        return False


def clear_cache_by_pattern(pattern: str) -> int:
    """
    根據模式刪除多個快取
    
    Parameters
    ----------
    pattern : str
        匹配模式，例如 "user:*" 將刪除所有以 "user:" 開頭的快取
        
    Returns
    -------
    int
        刪除的快取數量
    """
    if redis_client is None:
        logger.debug(f"Redis 處於模擬模式，無法刪除快取: {pattern}")
        return 0
    
    formatted_pattern = _format_key(pattern)
    
    try:
        # 獲取所有匹配的鍵
        keys = redis_client.keys(formatted_pattern)
        if not keys:
            return 0
        
        # 刪除這些鍵
        return redis_client.delete(*keys)
    except RedisError as e:
        logger.error(f"清除 Redis 快取時出錯: {str(e)}")
        return 0 