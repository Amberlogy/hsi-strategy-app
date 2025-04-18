"""
使用者策略綁定模組

提供使用者與策略之間的綁定關係管理，使用 Redis 存儲數據。
"""

import json
import logging
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

from app.core.redis_cache import get_cache, set_cache, delete_cache

# 配置日誌
logger = logging.getLogger(__name__)

# 策略緩存過期時間（秒）- 設置為 None 表示永不過期
STRATEGY_CACHE_TTL = None


def _get_user_strategy_key(user_id: str) -> str:
    """
    生成用戶策略的 Redis 鍵
    
    Parameters
    ----------
    user_id : str
        使用者 ID
        
    Returns
    -------
    str
        格式化的 Redis 鍵
    """
    return f"user:{user_id}:strategies"


def bind_strategy_to_user(user_id: str, strategy_id: str, config: Dict[str, Any]) -> bool:
    """
    將策略綁定到使用者
    
    Parameters
    ----------
    user_id : str
        使用者 ID
    strategy_id : str
        策略 ID
    config : Dict[str, Any]
        策略配置參數
        
    Returns
    -------
    bool
        綁定是否成功
    """
    key = _get_user_strategy_key(user_id)
    
    # 獲取使用者現有策略
    strategies = get_user_strategies(user_id) or []
    
    # 檢查策略是否已存在
    for strategy in strategies:
        if strategy.get("id") == strategy_id:
            # 更新現有策略配置
            strategy["config"] = config
            logger.info(f"更新使用者 {user_id} 的策略 {strategy_id} 配置")
            return set_cache(key, strategies, STRATEGY_CACHE_TTL)
    
    # 添加新策略
    new_strategy = {
        "id": strategy_id,
        "config": config,
        "bind_id": str(uuid.uuid4()),  # 生成綁定 ID
        "created_at": datetime.utcnow().isoformat()
    }
    strategies.append(new_strategy)
    
    logger.info(f"使用者 {user_id} 綁定新策略 {strategy_id}")
    return set_cache(key, strategies, STRATEGY_CACHE_TTL)


def get_user_strategies(user_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    獲取使用者綁定的所有策略
    
    Parameters
    ----------
    user_id : str
        使用者 ID
        
    Returns
    -------
    Optional[List[Dict[str, Any]]]
        使用者綁定的策略列表，如果不存在則返回 None
    """
    key = _get_user_strategy_key(user_id)
    strategies = get_cache(key)
    
    if strategies is None:
        logger.debug(f"使用者 {user_id} 沒有綁定任何策略")
        return []
    
    logger.debug(f"獲取到使用者 {user_id} 的 {len(strategies)} 個策略")
    return strategies


def unbind_strategy(user_id: str, bind_id: str) -> bool:
    """
    解除使用者與策略的綁定
    
    Parameters
    ----------
    user_id : str
        使用者 ID
    bind_id : str
        綁定 ID
        
    Returns
    -------
    bool
        解綁是否成功
    """
    key = _get_user_strategy_key(user_id)
    
    # 獲取使用者現有策略
    strategies = get_user_strategies(user_id)
    if not strategies:
        return False
    
    # 查找並移除指定 bind_id 的策略
    original_count = len(strategies)
    strategies = [s for s in strategies if s.get("bind_id") != bind_id]
    
    if len(strategies) == original_count:
        logger.warning(f"未找到使用者 {user_id} 的綁定 ID {bind_id}")
        return False
    
    # 更新策略列表或在沒有策略時刪除鍵
    if strategies:
        result = set_cache(key, strategies, STRATEGY_CACHE_TTL)
    else:
        result = delete_cache(key)
    
    logger.info(f"已解除使用者 {user_id} 的策略綁定 {bind_id}")
    return result 