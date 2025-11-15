"""
用户数据访问层
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, case
from datetime import datetime

from ..models.user import User
from ..models.session import Session


class UserRepository:
    """用户数据访问层"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        result = await self.db.execute(
            select(User).where(User.username == username, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email, User.is_deleted == False)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """根据用户名或邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(
                (User.username == identifier) | (User.email == identifier),
                User.is_deleted == False
            )
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: Optional[int] = None, limit: Optional[int] = None) -> List[User]:
        """获取用户列表"""
        # 定义角色权限排序（数字越小权限越高）
        role_order = case(
            (User.role == 'super_admin', 1),
            (User.role == 'admin', 2),
            (User.role == 'operator', 3),
            (User.role == 'viewer', 4),
            (User.role == 'user', 5),
            else_=6  # 未知角色排在最后
        )
        
        stmt = (
            select(User)
            .where(User.is_deleted == False)
            .order_by(
                role_order,  # 首先按角色权限排序（权限高到低）
                User.created_at.desc()  # 然后按创建时间排序（新到旧）
            )
        )
        if skip is not None and limit is not None:
            stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_total_count(self) -> int:
        """获取用户总数"""
        result = await self.db.execute(
            select(func.count(User.id)).where(User.is_deleted == False)
        )
        return result.scalar()
    
    async def create(self, user_data: dict) -> User:
        """创建用户"""
        user = User(**user_data)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User, update_data: dict) -> User:
        """更新用户"""
        for field, value in update_data.items():
            if hasattr(user, field):
                setattr(user, field, value)
        
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def soft_delete(self, user: User, deleted_by: str) -> bool:
        """软删除用户"""
        user.is_deleted = True
        user.updated_by = deleted_by
        user.updated_at = datetime.utcnow()
        await self.db.commit()
        return True
    
    async def username_exists(self, username: str, exclude_user_id: str = None) -> bool:
        """检查用户名是否存在"""
        query = select(User).where(User.username == username, User.is_deleted == False)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def email_exists(self, email: str, exclude_user_id: str = None) -> bool:
        """检查邮箱是否存在"""
        if not email:
            return False
            
        query = select(User).where(User.email == email, User.is_deleted == False)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def mobile_exists(self, mobile: str, exclude_user_id: str = None) -> bool:
        """检查手机号是否存在"""
        if not mobile:
            return False
            
        query = select(User).where(User.mobile == mobile, User.is_deleted == False)
        if exclude_user_id:
            query = query.where(User.id != exclude_user_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def invalidate_user_sessions(self, user_id: str) -> bool:
        """使用户的所有会话失效"""
        await self.db.execute(
            update(Session)
            .where(Session.user_id == user_id, Session.is_deleted == False)
            .values(is_deleted=True, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        return True
