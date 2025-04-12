"""
檢查 Redis 中的 hsi:* 鍵
"""

import os
import redis
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# 從環境變數讀取 Redis 連線設定
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None) or None  # 處理空字串的情況
REDIS_PREFIX = "hsi:"  # 前綴以區分不同應用的快取

try:
    # 連接到 Redis
    r = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD,
        decode_responses=True  # 自動將回應解碼為字符串
    )
    
    # 嘗試 ping Redis 伺服器
    if r.ping():
        print(f"成功連接到 Redis 伺服器: {REDIS_HOST}:{REDIS_PORT}")
    else:
        print("連接到 Redis 伺服器成功，但 ping 操作失敗")
    
    # 使用模式匹配搜索鍵
    keys = r.keys(f"{REDIS_PREFIX}*")
    
    if keys:
        print(f"找到 {len(keys)} 個 'hsi:*' 鍵:")
        for key in keys:
            # 獲取鍵的值類型
            key_type = r.type(key)
            print(f"鍵: {key}, 類型: {key_type}")
            
            # 如果是字符串類型，獲取其值
            if key_type == "string":
                value = r.get(key)
                print(f"  值: {value[:100]}..." if len(str(value)) > 100 else f"  值: {value}")
            
            # 如果是哈希類型，獲取其所有字段
            elif key_type == "hash":
                fields = r.hgetall(key)
                print(f"  字段數: {len(fields)}")
                for field, value in list(fields.items())[:3]:  # 只顯示前3個字段
                    print(f"    {field}: {value[:50]}..." if len(str(value)) > 50 else f"    {field}: {value}")
                if len(fields) > 3:
                    print(f"    ... 及其他 {len(fields) - 3} 個字段")
            
            # 獲取 TTL（生存時間）
            ttl = r.ttl(key)
            if ttl > 0:
                print(f"  TTL: {ttl} 秒")
            elif ttl == -1:
                print("  TTL: 永不過期")
            else:
                print("  TTL: 已過期或不存在")
            
            print()  # 空行分隔每個鍵的輸出
    else:
        print("未找到任何 'hsi:*' 鍵")

except redis.exceptions.ConnectionError as e:
    print(f"連接到 Redis 伺服器失敗: {e}")
except Exception as e:
    print(f"發生錯誤: {e}") 