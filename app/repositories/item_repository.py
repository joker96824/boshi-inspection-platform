"""
巡检项目数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..models.item import Item
from ..core.exceptions import ResourceNotFoundError


class ItemRepository:
    """巡检项目数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Item:
        """创建巡检项目"""
        item = Item(**data)
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def get_by_id(self, item_id: str) -> Optional[Item]:
        """根据ID获取巡检项目"""
        query = select(Item).where(Item.id == item_id, Item.is_deleted == False)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, item_ids: List[str]) -> List[Item]:
        """根据ID列表获取巡检项目"""
        if not item_ids:
            return []
        
        query = select(Item).where(
            Item.id.in_(item_ids),
            Item.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                     item_name: str = None) -> Tuple[List[Item], int]:
        """获取巡检项目列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [Item.is_deleted == False]
        
        if item_name:
            conditions.append(Item.item_name.like(f"%{item_name}%"))
        
        # 查询总数
        count_query = select(func.count(Item.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(Item)
                .where(and_(*conditions))
                .order_by(Item.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        items = list(result.scalars().all())
        
        return items, total
    
    async def update(self, item_id: str, data: Dict[str, Any]) -> Optional[Item]:
        """更新巡检项目"""
        item = await self.get_by_id(item_id)
        if not item:
            raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
        
        for key, value in data.items():
            setattr(item, key, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def soft_delete(self, item_id: str, deleted_by: str) -> bool:
        """软删除巡检项目"""
        item = await self.get_by_id(item_id)
        if not item:
            return False
        
        item.is_deleted = True
        item.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def exists_by_name(self, item_name: str, exclude_item_id: str = None) -> bool:
        """检查巡检项目名是否已存在"""
        conditions = [
            Item.item_name == item_name,
            Item.is_deleted == False
        ]
        if exclude_item_id:
            conditions.append(Item.id != exclude_item_id)
        
        query = select(Item).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_all(self) -> int:
        """统计所有巡检项目数量"""
        stmt = select(func.count(Item.id)).where(Item.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
