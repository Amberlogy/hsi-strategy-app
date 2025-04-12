"""
使用者資料模型定義
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from uuid import uuid4

class Strategy(BaseModel):
    """使用者儲存的策略模型"""
    id: str
    name: str
    type: str
    parameters: dict
    created_at: str

class User(BaseModel):
    """基本使用者模型"""
    id: str = Field(default_factory=lambda: str(uuid4()))
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    full_name: Optional[str] = None
    disabled: Optional[bool] = False
    strategies: Optional[List[Strategy]] = []

class UserInDB(User):
    """資料庫中的使用者模型"""
    pass

class UserCreate(BaseModel):
    """使用者註冊模型"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserUpdate(BaseModel):
    """使用者資料更新模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    """使用者登入模型"""
    username: str
    password: str

class UserInLogin(BaseModel):
    """使用者登入輸入模型"""
    username: str
    password: str

class UserInRegister(BaseModel):
    """使用者註冊輸入模型"""
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    full_name: Optional[str] = None 