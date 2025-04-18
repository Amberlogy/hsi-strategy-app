"""
Redis 快取測試腳本
"""

import json
import time
from redis_cache import get_cache, set_cache, delete_cache, clear_cache_by_pattern

def test_redis_cache():
    """測試 Redis 快取功能"""
    print("開始測試 Redis 快取模組...")
    
    # 測試數據
    test_key = "test:key"
    test_value = {
        "name": "恒生指數",
        "code": "HSI",
        "data": [26500, 26600, 26550, 26700, 26650],
        "timestamp": time.time()
    }
    
    # 測試設置快取
    print(f"\n1. 測試設置快取，鍵：{test_key}")
    result = set_cache(test_key, test_value)
    print(f"   設置結果：{result}")
    
    # 測試獲取快取
    print(f"\n2. 測試獲取快取，鍵：{test_key}")
    value = get_cache(test_key)
    print(f"   獲取結果：{json.dumps(value, ensure_ascii=False, indent=2)}")
    
    # 檢查值是否一致
    print(f"\n3. 檢查快取值是否與原始值一致")
    is_equal = value == test_value
    print(f"   一致性檢查：{'通過' if is_equal else '失敗'}")
    
    # 測試刪除快取
    print(f"\n4. 測試刪除快取，鍵：{test_key}")
    delete_result = delete_cache(test_key)
    print(f"   刪除結果：{delete_result}")
    
    # 確認快取已被刪除
    print(f"\n5. 確認快取已被刪除")
    deleted_value = get_cache(test_key)
    print(f"   刪除後獲取結果：{deleted_value}")
    
    # 測試模式匹配刪除
    print(f"\n6. 測試模式匹配刪除")
    # 先設置幾個相關的鍵
    set_cache("test:a", "A")
    set_cache("test:b", "B")
    set_cache("test:c", "C")
    
    # 使用模式刪除
    count = clear_cache_by_pattern("test:*")
    print(f"   匹配刪除數量：{count}")
    
    print("\n測試完成!")


if __name__ == "__main__":
    test_redis_cache() 