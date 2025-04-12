"""
使用者身份驗證與JWT相關邏輯
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import jwt as pyjwt

from app.users.models import User
from app.users.db import fake_users_db, init_test_user

# JWT設定
SECRET_KEY = "your-secret-key-for-jwt"  # 生產環境應使用環境變數
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24小時

# 密碼工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/token")

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# 密碼處理函數
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """驗證密碼"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """產生密碼的雜湊值"""
    return pwd_context.hash(password)

# 初始化測試用戶（在定義get_password_hash之後）
init_test_user(get_password_hash)

# 使用者驗證函數
async def get_user(username: str) -> Optional[User]:
    """從資料庫取得使用者資料"""
    # 使用共用的fake_users_db
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return User(**user_dict)
    return None

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """驗證使用者帳號密碼"""
    user = await get_user(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

# JWT令牌相關函數
def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """創建JWT令牌

    Args:
        data: 要編碼到令牌中的數據
        expires_delta: 令牌過期時間，預設為1天

    Returns:
        str: JWT令牌字符串
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # 使用python-jose
    # encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 使用pyjwt
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """驗證令牌並解析出payload數據

    Args:
        token: JWT令牌字符串

    Returns:
        Dict[str, Any]: 解析出的payload數據

    Raises:
        HTTPException: 如果令牌無效或已過期
    """
    try:
        # 使用pyjwt解碼令牌
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已過期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except pyjwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌無效",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """從令牌取得當前使用者"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="認證失敗",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 使用verify_token函數驗證和解析令牌
        payload = verify_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except (JWTError, HTTPException):
        raise credentials_exception
    
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """檢查使用者帳戶是否啟用"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="帳戶已停用")
    return current_user 