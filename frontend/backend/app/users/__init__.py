"""
使用者模組
包含使用者註冊、登入、認證與策略綁定功能
"""

from app.users.models import (
    User, UserInDB, UserCreate, Strategy, UserUpdate,
    UserInLogin, UserInRegister
)
from app.users.auth import (
    Token, TokenData,
    get_current_active_user, 
    create_access_token, 
    authenticate_user,
    get_password_hash,
    verify_token
)
from app.users.db import fake_users_db, init_test_user
from app.users.strategy_link import (
    bind_strategy_to_user,
    get_user_strategies,
    unbind_strategy
)

__all__ = [
    # 模型
    "User", 
    "UserInDB", 
    "UserCreate", 
    "UserUpdate",
    "Strategy",
    "UserInLogin",
    "UserInRegister",
    # 認證
    "Token",
    "TokenData",
    "get_current_active_user", 
    "create_access_token", 
    "authenticate_user",
    "get_password_hash",
    "verify_token",
    # 數據庫
    "fake_users_db",
    "init_test_user",
    # 策略綁定
    "bind_strategy_to_user",
    "get_user_strategies",
    "unbind_strategy"
] 