"""
厂区数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.factory import Factory
from ..core.exceptions import ResourceNotFoundError


class FactoryRepository:
    """厂区数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Factory:
        """创建厂区"""
        factory = Factory(**data)
        self.db.add(factory)
        await self.db.commit()
        await self.db.refresh(factory)
        return factory
    
    async def get_by_id(self, factory_id: str) -> Optional[Factory]:
        """根据ID获取厂区"""
        stmt = select(Factory).where(
            Factory.id == factory_id,
            Factory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None, 
                      factory_name: str = None) -> Tuple[List[Factory], int]:
        """获取厂区列表"""
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size
        conditions = [Factory.is_deleted == False]
        
        if factory_name is not None:
            conditions.append(Factory.factory_name.like(f"%{factory_name}%"))
        
        # 查询总数
        count_query = select(func.count(Factory.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(Factory)
                .where(and_(*conditions))
                .order_by(Factory.created_at.desc()))
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        factories = list(result.scalars().all())
        return factories, total
    
    async def get_by_ids(self, factory_ids: List[str]) -> List[Factory]:
        """根据ID列表获取厂区"""
        stmt = select(Factory).where(
            Factory.id.in_(factory_ids),
            Factory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, factory_id: str, data: Dict[str, Any]) -> Optional[Factory]:
        """更新厂区"""
        stmt = select(Factory).where(
            Factory.id == factory_id,
            Factory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        factory = result.scalar_one_or_none()
        
        if not factory:
            return None
        
        for key, value in data.items():
            if hasattr(factory, key):
                setattr(factory, key, value)
        
        await self.db.commit()
        await self.db.refresh(factory)
        return factory
    
    async def soft_delete(self, factory_id: str, updated_by: str) -> bool:
        """软删除厂区"""
        stmt = select(Factory).where(
            Factory.id == factory_id,
            Factory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        factory = result.scalar_one_or_none()
        
        if not factory:
            return False
        
        factory.is_deleted = True
        factory.updated_by = updated_by
        await self.db.commit()
        return True
    
    async def exists_by_name(self, factory_name: str, exclude_id: str = None) -> bool:
        """检查厂区名是否已存在"""
        conditions = [
            Factory.factory_name == factory_name,
            Factory.is_deleted == False
        ]
        
        if exclude_id:
            conditions.append(Factory.id != exclude_id)
        
        stmt = select(Factory).where(and_(*conditions))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

