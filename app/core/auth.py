"""
认证相关功能
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from ..config.settings import settings
from ..models.user import User
from ..models.session import Session
from ..core.deps import get_db
from ..core.exceptions import (
    TokenError, UserNotFoundError
)

# JWT配置
security = HTTPBearer()


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """创建刷新令牌"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """验证令牌"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise TokenError("无效的令牌")


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: AsyncSession = Depends(get_db)
) -> Optional[dict]:
    """获取当前用户信息（可选认证）"""
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            return None
    except JWTError:
        return None

    # 查询用户信息
    stmt = select(User).where(User.id == user_id, User.is_deleted == False)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        return None

    # 检查当前令牌的会话是否有效
    from ..models.session import Session
    from datetime import datetime
    
    session_stmt = select(Session).where(
        Session.token == token,
        Session.user_id == user_id,
        Session.is_deleted == False,
        Session.expires_at > datetime.utcnow()
    )
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()
    
    if session is None:
        return None

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "mobile": user.mobile,
        "role": user.role
    }


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> dict:
    """获取当前用户信息"""
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise TokenError("无效的认证信息")
    except JWTError:
        raise TokenError("无效的认证信息")

    # 查询用户信息
    stmt = select(User).where(User.id == user_id, User.is_deleted == False)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        raise UserNotFoundError(user_id)

    # 检查当前令牌的会话是否有效
    from ..models.session import Session
    from datetime import datetime
    
    session_stmt = select(Session).where(
        Session.token == token,
        Session.user_id == user_id,
        Session.is_deleted == False,
        Session.expires_at > datetime.utcnow()
    )
    session_result = await db.execute(session_stmt)
    session = session_result.scalar_one_or_none()
    
    if session is None:
        raise TokenError("会话已失效，请重新登录")

    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "mobile": user.mobile,
        "role": user.role
    }


# require_admin 已移动到 permissions.py 中


def get_token_payload(token: str) -> Dict[str, Any]:
    """获取令牌载荷"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise TokenError("无效的令牌")


def is_token_expired(token: str) -> bool:
    """检查令牌是否过期"""
    try:
        payload = get_token_payload(token)
        exp = payload.get("exp")
        if exp is None:
            return True
        
        return datetime.utcnow().timestamp() > exp
    except AuthenticationError:
        return True


def get_token_expiration(token: str) -> Optional[datetime]:
    """获取令牌过期时间"""
    try:
        payload = get_token_payload(token)
        exp = payload.get("exp")
        if exp is None:
            return None
        
        return datetime.fromtimestamp(exp)
    except AuthenticationError:
        return None


def create_token_pair(user_id: str, username: str) -> Dict[str, str]:
    """创建令牌对"""
    access_token = create_access_token(
        data={"sub": str(user_id), "username": username}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user_id), "username": username}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
