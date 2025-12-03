"""
分组数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.group import Group
from ..core.exceptions import ResourceNotFoundError


class GroupRepository:
    """分组数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Group:
        """创建分组"""
        group = Group(**data)
        self.db.add(group)
        await self.db.commit()
        await self.db.refresh(group)
        return group
    
    async def get_by_id(self, group_id: str) -> Optional[Group]:
        """根据ID获取分组"""
        query = (select(Group)
                .where(Group.id == group_id, Group.is_deleted == False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        page: Optional[int] = None,
        size: Optional[int] = None,
        group_name: Optional[str] = None,
    ) -> Tuple[List[Group], int]:
        """获取分组列表"""
        query = select(Group).where(Group.is_deleted == False)
        
        # 应用筛选条件
        if group_name:
            query = query.where(Group.group_name.like(f"%{group_name}%"))
        
        # 排序
        query = query.order_by(Group.created_at.desc(), Group.id.asc())
        
        # 获取总数
        count_query = select(func.count()).select_from(Group).where(Group.is_deleted == False)
        if group_name:
            count_query = count_query.where(Group.group_name.like(f"%{group_name}%"))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 分页
        if page is not None and size is not None:
            offset = (page - 1) * size
            query = query.offset(offset).limit(size)
        
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def update(self, group_id: str, data: Dict[str, Any]) -> Optional[Group]:
        """更新分组"""
        group = await self.get_by_id(group_id)
        if not group:
            return None
        
        for key, value in data.items():
            if hasattr(group, key):
                setattr(group, key, value)
        
        await self.db.commit()
        await self.db.refresh(group)
        return group
    
    async def delete(self, group_id: str, user: dict) -> bool:
        """软删除分组"""
        group = await self.get_by_id(group_id)
        if not group:
            return False
        
        group.is_deleted = True
        group.updated_by = user.get("username")
        await self.db.commit()
        return True
    
    async def exists_by_name(self, group_name: str, exclude_id: Optional[str] = None) -> bool:
        """检查名称是否存在"""
        query = select(Group).where(
            Group.group_name == group_name,
            Group.is_deleted == False
        )
        if exclude_id:
            query = query.where(Group.id != exclude_id)
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

