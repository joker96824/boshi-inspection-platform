"""
云台预设点数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.gimbalpresetpoint import GimbalPresetPoint
from ..core.exceptions import ResourceNotFoundError


class GimbalPresetPointRepository:
    """云台预设点数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> GimbalPresetPoint:
        """创建云台预设点"""
        preset_point = GimbalPresetPoint(**data)
        self.db.add(preset_point)
        await self.db.commit()
        await self.db.refresh(preset_point)
        return preset_point
    
    async def get_by_id(self, preset_point_id: str) -> Optional[GimbalPresetPoint]:
        """根据ID获取云台预设点"""
        query = (
            select(GimbalPresetPoint)
            .options(
                selectinload(GimbalPresetPoint.gimbal),
                selectinload(GimbalPresetPoint.inspection_projects),
            )
            .where(GimbalPresetPoint.id == preset_point_id, GimbalPresetPoint.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, preset_point_ids: List[str]) -> List[GimbalPresetPoint]:
        """根据ID列表获取云台预设点"""
        if not preset_point_ids:
            return []
        
        query = (
            select(GimbalPresetPoint)
            .options(
                selectinload(GimbalPresetPoint.gimbal),
            )
            .where(
                GimbalPresetPoint.id.in_(preset_point_ids),
                GimbalPresetPoint.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None, 
                     preset_name: str = None, gimbal_id: str = None,
                     sort_by: str = "created_at", sort_order: str = "desc") -> Tuple[List[GimbalPresetPoint], int]:
        """获取云台预设点列表"""
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size
        
        # 构建查询条件
        conditions = [GimbalPresetPoint.is_deleted == False]
        
        if preset_name:
            conditions.append(GimbalPresetPoint.preset_name.like(f"%{preset_name}%"))
        
        if gimbal_id:
            conditions.append(GimbalPresetPoint.gimbal_id == gimbal_id)
        
        # 查询总数
        count_query = select(func.count(GimbalPresetPoint.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 构建排序
        order_column = getattr(GimbalPresetPoint, sort_by, GimbalPresetPoint.created_at)
        if sort_order == "desc":
            order_column = order_column.desc()
        else:
            order_column = order_column.asc()
        
        # 查询数据
        query = (
            select(GimbalPresetPoint)
            .options(
                selectinload(GimbalPresetPoint.gimbal),
            )
            .where(and_(*conditions))
            .order_by(order_column)
        )
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        preset_points = list(result.scalars().all())
        
        return preset_points, total
    
    async def get_by_gimbal_id(self, gimbal_id: str) -> List[GimbalPresetPoint]:
        """根据云台ID获取预设点列表"""
        query = (
            select(GimbalPresetPoint)
            .where(
                GimbalPresetPoint.gimbal_id == gimbal_id,
                GimbalPresetPoint.is_deleted == False
            )
            .order_by(GimbalPresetPoint.created_at.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def update(self, preset_point_id: str, data: Dict[str, Any]) -> Optional[GimbalPresetPoint]:
        """更新云台预设点"""
        preset_point = await self.get_by_id(preset_point_id)
        if not preset_point:
            raise ResourceNotFoundError(f"云台预设点ID '{preset_point_id}' 不存在")
        
        for key, value in data.items():
            setattr(preset_point, key, value)
        
        await self.db.commit()
        await self.db.refresh(preset_point)
        return preset_point
    
    async def soft_delete(self, preset_point_id: str, deleted_by: str) -> bool:
        """软删除云台预设点"""
        preset_point = await self.get_by_id(preset_point_id)
        if not preset_point:
            return False
        
        preset_point.is_deleted = True
        preset_point.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def exists_by_name(self, preset_name: str, gimbal_id: str, exclude_preset_point_id: str = None) -> bool:
        """检查预设点名称是否已存在"""
        conditions = [
            GimbalPresetPoint.preset_name == preset_name,
            GimbalPresetPoint.gimbal_id == gimbal_id,
            GimbalPresetPoint.is_deleted == False
        ]
        if exclude_preset_point_id:
            conditions.append(GimbalPresetPoint.id != exclude_preset_point_id)
        
        query = select(GimbalPresetPoint).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    async def count_all(self) -> int:
        """统计所有云台预设点数量"""
        stmt = select(func.count(GimbalPresetPoint.id)).where(GimbalPresetPoint.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

