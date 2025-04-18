"""
測試 Redis 快取模組

測試 set_cache() 寫入一個 key 後，get_cache() 能夠正確取出並驗證內容相符
"""

import sys
import os
import pytest
import uuid

# 添加項目根目錄到 Python 路徑
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.core.redis_cache import set_cache, get_cache, delete_cache, redis_client

# 跳過測試如果無法連接到 Redis
pytestmark = pytest.mark.skipif(
    redis_client is None,
    reason="無法連接到 Redis 伺服器"
)


def test_set_and_get_cache():
    """
    測試 set_cache() 寫入一個 key 後，get_cache() 能夠正確取出並驗證內容相符
    """
    # 生成唯一的測試鍵名，避免衝突
    test_key = f"test_cache_{uuid.uuid4().hex}"
    
    try:
        # 準備測試數據
        test_value = {
            "string": "測試字串",
            "number": 42,
            "nested": {
                "key": "value"
            }
        }
        
        # 使用 set_cache() 寫入數據
        set_result = set_cache(test_key, test_value)
        
        # 驗證設置成功
        assert set_result is True, "設置快取應該成功"
        
        # 使用 get_cache() 讀取數據
        cached_value = get_cache(test_key)
        
        # 驗證讀取的數據與寫入的數據相符
        assert cached_value is not None, "應該能夠獲取到快取的值"
        assert cached_value == test_value, "獲取的值應該與設置的值相同"
        
        # 驗證數據類型
        assert isinstance(cached_value, dict), "獲取的值應該是字典類型"
        assert cached_value["string"] == "測試字串", "字串值應該相符"
        assert cached_value["number"] == 42, "數字值應該相符"
        assert cached_value["nested"]["key"] == "value", "嵌套值應該相符"

    finally:
        # 測試完成後清理
        delete_cache(test_key) 