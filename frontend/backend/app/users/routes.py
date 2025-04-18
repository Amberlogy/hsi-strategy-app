"""
使用者相關路由定義
"""

from datetime import timedelta
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm

from app.users.models import (
    User, UserCreate, UserInDB, UserUpdate, Strategy, 
    UserInLogin, UserInRegister
)
from app.users.auth import (
    Token, TokenData, 
    get_current_active_user, authenticate_user, create_access_token,
    get_password_hash, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
)
from app.users.db import fake_users_db
from app.users.strategy_link import bind_strategy_to_user, get_user_strategies, unbind_strategy

router = APIRouter(tags=["使用者"])

@router.post("/register", response_model=Dict[str, Any])
async def register_user(user_data: UserInRegister):
    """註冊新使用者並回傳JWT令牌
    
    Args:
        user_data: 包含用戶名、密碼和確認密碼的註冊數據
        
    Returns:
        Dict: 包含JWT令牌、令牌類型和用戶資訊
    """
    # 檢查密碼是否一致
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密碼不一致"
        )
    
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="使用者名稱已存在"
        )
    
    # 創建使用者並儲存
    hashed_password = get_password_hash(user_data.password)
    user_in_db = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        strategies=[]
    )
    fake_users_db[user_data.username] = user_in_db.dict()
    
    # 創建訪問令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.username}, expires_delta=access_token_expires
    )
    
    # 返回令牌和使用者資訊（不含密碼）
    user_data = user_in_db.dict()
    user_data.pop("hashed_password", None)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

@router.post("/login", response_model=Dict[str, Any])
async def login_user(form_data: UserInLogin):
    """使用者登入取得令牌
    
    Args:
        form_data: 包含用戶名和密碼的登入數據
        
    Returns:
        Dict: 包含JWT令牌、令牌類型和用戶資訊
    """
    # 使用authenticate_user函數驗證使用者
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 創建訪問令牌
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # 返回令牌和使用者資訊（不含密碼）
    user_data = user.dict()
    user_data.pop("hashed_password", None)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

# 保留相容性，支援OAuth2PasswordRequestForm
@router.post("/token", response_model=Token)
async def login_using_form(form_data: OAuth2PasswordRequestForm = Depends()):
    """使用表單登入取得令牌 (OAuth2相容模式)"""
    login_data = UserInLogin(username=form_data.username, password=form_data.password)
    result = await login_user(login_data)
    return {"access_token": result["access_token"], "token_type": result["token_type"]}

@router.get("/me", response_model=Dict[str, Any])
async def get_user_me(current_user: User = Depends(get_current_active_user)):
    """取得目前登入的使用者資料
    
    此端點使用 JWT 令牌驗證用戶身份，並返回當前用戶的基本資料。
    需要在請求標頭中提供有效的Bearer令牌。
    
    Authorization: Bearer <token>
    
    Returns:
        Dict: 包含使用者基本資料的字典，不含敏感資訊
    
    Raises:
        401 Unauthorized: 如果令牌無效或已過期
        400 Bad Request: 如果用戶帳戶已被停用
    """
    # 返回使用者資訊（不含密碼）
    user_data = current_user.dict()
    user_data.pop("hashed_password", None)
    
    return {
        "status": "success",
        "message": "成功獲取用戶資料",
        "user": user_data
    }

@router.put("/me", response_model=Dict[str, Any])
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_active_user)):
    """更新目前登入的使用者資料"""
    username = current_user.username
    if username not in fake_users_db:
        raise HTTPException(status_code=404, detail="使用者不存在")
    
    # 更新使用者資料
    stored_user = fake_users_db[username]
    stored_user_model = User(**stored_user)
    update_data = user_update.dict(exclude_unset=True)
    
    # 處理密碼更新
    if "password" in update_data:
        hashed_password = get_password_hash(update_data["password"])
        update_data["hashed_password"] = hashed_password
        del update_data["password"]
    
    # 更新使用者資料
    updated_user = stored_user_model.copy(update=update_data)
    fake_users_db[username] = updated_user.dict()
    
    # 返回不包含密碼的使用者資料
    user_data = updated_user.dict()
    user_data.pop("hashed_password", None)
    
    return {
        "status": "success",
        "message": "使用者資料更新成功",
        "user": user_data
    }

# 原有的策略API路由
@router.get("/me/strategies", response_model=Dict[str, Any])
async def get_current_user_strategies(current_user: User = Depends(get_current_active_user)):
    """取得目前登入使用者的策略列表
    
    返回使用者綁定的所有策略列表，包含策略ID和配置
    
    Returns:
        Dict: 包含策略列表的字典
    """
    strategies = get_user_strategies(current_user.id)
    
    return {
        "status": "success",
        "count": len(strategies),
        "strategies": strategies
    }

@router.post("/me/strategies", response_model=Dict[str, Any])
async def bind_strategy(
    strategy_data: Dict[str, Any], 
    current_user: User = Depends(get_current_active_user)
):
    """為當前使用者綁定策略
    
    Args:
        strategy_data: 包含策略ID和配置的數據
        
    Returns:
        Dict: 操作結果
    """
    if "id" not in strategy_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少策略ID"
        )
    
    strategy_id = strategy_data["id"]
    config = strategy_data.get("config", {})
    
    result = bind_strategy_to_user(current_user.id, strategy_id, config)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="綁定策略失敗"
        )
    
    return {
        "status": "success",
        "message": f"成功綁定策略 {strategy_id}",
        "strategy_id": strategy_id
    }

@router.delete("/me/strategies/{bind_id}", response_model=Dict[str, Any])
async def remove_strategy_binding(
    bind_id: str, 
    current_user: User = Depends(get_current_active_user)
):
    """解除當前使用者與指定策略的綁定
    
    Args:
        bind_id: 綁定ID
        
    Returns:
        Dict: 操作結果
    """
    result = unbind_strategy(current_user.id, bind_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到指定的策略綁定"
        )
    
    return {
        "status": "success",
        "message": "成功解除策略綁定",
        "bind_id": bind_id
    }

# 新的策略API路由
@router.get("/strategies", response_model=Dict[str, Any])
async def list_user_strategies(current_user: User = Depends(get_current_active_user)):
    """列出目前登入者所有已綁定策略
    
    此端點使用 JWT 令牌驗證用戶身份，並返回該用戶綁定的所有策略。
    
    Returns:
        Dict: 包含策略列表的字典
        
    Raises:
        401 Unauthorized: 如果令牌無效或已過期
    """
    strategies = get_user_strategies(current_user.id)
    
    return {
        "status": "success",
        "message": "成功獲取使用者策略列表",
        "count": len(strategies),
        "strategies": strategies
    }

@router.post("/bind-strategy", response_model=Dict[str, Any])
async def bind_user_strategy(
    strategy_data: Dict[str, Any],
    current_user: User = Depends(get_current_active_user)
):
    """綁定策略給目前登入者
    
    此端點用於將指定策略與設定綁定到當前登入用戶，需要JWT驗證。
    
    Args:
        strategy_data: 包含策略ID和設定的字典，格式：{"strategy_id": "...", "config": {...}}
        
    Returns:
        Dict: 操作結果
        
    Raises:
        400 Bad Request: 如果缺少必要參數
        401 Unauthorized: 如果令牌無效或已過期
        500 Internal Server Error: 如果綁定過程發生錯誤
    """
    # 檢查必要參數
    if "strategy_id" not in strategy_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="缺少策略ID (strategy_id)"
        )
    
    strategy_id = strategy_data["strategy_id"]
    config = strategy_data.get("config", {})
    
    # 執行綁定
    result = bind_strategy_to_user(current_user.id, strategy_id, config)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="綁定策略失敗"
        )
    
    # 獲取更新後的策略列表
    strategies = get_user_strategies(current_user.id)
    
    # 找出剛綁定的策略
    bound_strategy = None
    for strategy in strategies:
        if strategy.get("id") == strategy_id:
            bound_strategy = strategy
            break
    
    return {
        "status": "success",
        "message": f"成功綁定策略 {strategy_id}",
        "strategy": bound_strategy
    }

@router.post("/verify-token", response_model=Dict[str, Any])
async def verify_token_endpoint(token: str):
    """驗證JWT令牌並返回其Payload

    此端點用於測試JWT令牌的有效性，並返回令牌中包含的資料。
    """
    return verify_token(token) 