"""
使用者資料存儲模組
實際專案應改用資料庫而非記憶體存儲
"""

from typing import Dict, Any
from datetime import datetime
from uuid import uuid4

# 全域暫存使用者資料庫
fake_users_db: Dict[str, Dict[str, Any]] = {}

def init_test_user(password_hash_func) -> None:
    """初始化測試用戶，如果不存在"""
    if "test_user" not in fake_users_db:
        fake_users_db["test_user"] = {
            "id": str(uuid4()),  # 生成唯一ID
            "username": "test_user",
            "email": "user@example.com",
            "hashed_password": password_hash_func("testpassword"),
            "full_name": "測試使用者",
            "created_at": datetime.utcnow(),  # 使用當前時間
            "disabled": False,
            "strategies": []
        } 