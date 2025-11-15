"""
云台数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.gimbal import Gimbal
from ..models.gimbaltask import GimbalTask
from ..core.exceptions import ResourceNotFoundError


class GimbalRepository:
    """云台数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Gimbal:
        """创建云台"""
        gimbal = Gimbal(**data)
        self.db.add(gimbal)
        await self.db.commit()
        await self.db.refresh(gimbal)
        return gimbal
    
    async def get_by_id(self, gimbal_id: str) -> Optional[Gimbal]:
        """根据ID获取云台（预加载任务和日程）"""
        query = (
            select(Gimbal)
            .options(
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.schedules),
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.inspection_projects),
            )
            .where(Gimbal.id == gimbal_id, Gimbal.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, gimbal_ids: List[str]) -> List[Gimbal]:
        """根据ID列表获取云台（预加载任务和日程）"""
        if not gimbal_ids:
            return []
        
        query = (
            select(Gimbal)
            .options(
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.schedules),
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.inspection_projects),
            )
            .where(
                Gimbal.id.in_(gimbal_ids),
                Gimbal.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, 
                     gimbal_name: str = None, map_id: str = None,
                     sort_by: str = "created_at", sort_order: str = "desc") -> Tuple[List[Gimbal], int]:
        """获取云台列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [Gimbal.is_deleted == False]
        
        if gimbal_name:
            conditions.append(Gimbal.gimbal_name.like(f"%{gimbal_name}%"))
        
        if map_id:
            conditions.append(Gimbal.map_id == map_id)
        
        # 查询总数
        count_query = select(func.count(Gimbal.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 构建排序
        order_column = getattr(Gimbal, sort_by, Gimbal.created_at)
        if sort_order == "desc":
            order_column = order_column.desc()
        else:
            order_column = order_column.asc()
        
        # 查询数据（预加载任务和日程）
        query = (
            select(Gimbal)
            .options(
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.schedules),
                selectinload(Gimbal.gimbal_tasks).selectinload(GimbalTask.inspection_projects),
            )
            .where(and_(*conditions))
            .order_by(order_column)
            .offset(skip)
            .limit(size)
        )
        
        result = await self.db.execute(query)
        gimbals = list(result.scalars().all())
        
        return gimbals, total
    
    async def update(self, gimbal_id: str, data: Dict[str, Any]) -> Optional[Gimbal]:
        """更新云台"""
        gimbal = await self.get_by_id(gimbal_id)
        if not gimbal:
            raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
        
        for key, value in data.items():
            setattr(gimbal, key, value)
        
        await self.db.commit()
        await self.db.refresh(gimbal)
        return gimbal
    
    async def soft_delete(self, gimbal_id: str, deleted_by: str) -> bool:
        """软删除云台"""
        gimbal = await self.get_by_id(gimbal_id)
        if not gimbal:
            return False
        
        gimbal.is_deleted = True
        gimbal.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def exists_by_name(self, gimbal_name: str, exclude_gimbal_id: str = None) -> bool:
        """检查云台名是否已存在"""
        conditions = [
            Gimbal.gimbal_name == gimbal_name,
            Gimbal.is_deleted == False
        ]
        if exclude_gimbal_id:
            conditions.append(Gimbal.id != exclude_gimbal_id)
        
        query = select(Gimbal).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_all(self) -> int:
        """统计所有云台数量"""
        stmt = select(func.count(Gimbal.id)).where(Gimbal.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

