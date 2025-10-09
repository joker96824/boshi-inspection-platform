"""
会话相关Pydantic模式
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from .base import BaseResponse


class SessionBase(BaseResponse):
    """会话基础模式"""
    user_id: str = Field(..., description="用户ID")
    token: str = Field(..., description="会话令牌")
    expires_at: datetime = Field(..., description="过期时间")


class SessionCreate(SessionBase):
    """会话创建模式"""
    pass


class SessionResponse(SessionBase):
    """会话响应模式"""
    pass