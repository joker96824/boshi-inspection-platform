"""
认证业务逻辑层
"""

from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from ..repositories.user_repository import UserRepository
from ..core.security import verify_password
from ..core.auth import create_access_token
from ..core.exceptions import LoginFailedError, UserNotFoundError
from ..config.settings import settings
from ..models.session import Session
from ..utils.response import ApiResponse
from ..config.logging import log_user_action


class AuthService:
    """认证业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def login(self, username: str, password: str) -> dict:
        """用户登录"""
        # 查找用户
        user = await self.user_repo.get_by_username_or_email(username)
        if not user:
            # 记录登录失败日志
            log_user_action(
                user=username,
                action="登录",
                result="失败",
                details="用户不存在"
            )
            raise UserNotFoundError(username)
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            # 记录登录失败日志
            log_user_action(
                user=username,
                action="登录",
                result="失败", 
                details="密码错误"
            )
            raise LoginFailedError("用户名或密码错误")
        
        # 检查用户是否被删除
        if user.is_deleted:
            # 记录登录失败日志
            log_user_action(
                user=username,
                action="登录",
                result="失败",
                details="用户已被删除"
            )
            raise LoginFailedError("用户账户不存在")
        
        # 标记现有会话为已删除
        await self.user_repo.invalidate_user_sessions(user.id)
        
        # 创建新的访问令牌
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        # 创建新的会话记录
        session = Session(
            user_id=user.id,
            token=access_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(session)
        
        # 更新用户最后登录时间
        user.last_login_at = datetime.utcnow()
        await self.db.commit()
        
        # 记录登录成功的业务日志
        log_user_action(
            user=user.username,
            action="登录",
            result="成功",
            details=f"角色: {user.role}"
        )
        
        return ApiResponse.success(
            data={
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "mobile": user.mobile,
                    "role": user.role,
                    "last_login_at": user.last_login_at
                },
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 3600
            },
            message="登录成功"
        )
    
    async def logout(self, user_id: str) -> dict:
        """用户登出"""
        await self.user_repo.invalidate_user_sessions(user_id)
        return ApiResponse.success(message="登出成功")
    
    async def refresh_token(self, current_user: dict) -> dict:
        """刷新令牌"""
        user_id = current_user["id"]
        
        # 查找用户
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)
        
        # 标记现有会话为已删除
        await self.user_repo.invalidate_user_sessions(user_id)
        
        # 创建新的访问令牌
        new_access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        # 创建新的会话记录
        new_session = Session(
            user_id=user.id,
            token=new_access_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.ACCESS_TOKEN_EXPIRE_DAYS),
        )
        self.db.add(new_session)
        await self.db.commit()
        
        return ApiResponse.success(
            data={
                "access_token": new_access_token,
                "token_type": "bearer",
                "expires_in": settings.ACCESS_TOKEN_EXPIRE_DAYS * 24 * 3600
            },
            message="令牌刷新成功"
        )
