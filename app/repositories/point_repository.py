"""
巡检点数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from ..models.point import Point
from ..models.device import Device
from ..models.item import Item
from ..config.logging import get_logger

logger = get_logger(__name__)


class PointRepository:
    """巡检点数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> Point:
        """创建巡检点"""
        point = Point(**data)
        self.db.add(point)
        await self.db.commit()
        await self.db.refresh(point)
        return point
    
    async def get_by_id(self, point_id: str) -> Optional[Point]:
        """根据ID获取巡检点（预加载设备和巡检项目）"""
        stmt = (
            select(Point)
            .options(
                selectinload(Point.devices).selectinload(Device.items),
                selectinload(Point.devices).selectinload(Device.sensors)
            )
            .where(
                Point.id == point_id,
                Point.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, point_ids: List[str]) -> List[Point]:
        """根据ID列表获取巡检点"""
        query = select(Point).where(
            Point.id.in_(point_ids),
            Point.is_deleted == False
        ).order_by(Point.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_by_map_id(self, map_id: str, page: int = 1, size: int = 20, point_name: str = None) -> tuple[List[Point], int]:
        """根据地图ID获取巡检点列表"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [
            Point.map_id == map_id,
            Point.is_deleted == False
        ]
        
        # 添加巡检点名称模糊匹配条件
        if point_name:
            conditions.append(Point.point_name.like(f"%{point_name}%"))
        
        # 查询总数
        count_stmt = select(func.count(Point.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据
        stmt = select(Point).where(*conditions).order_by(Point.created_at.desc()).offset(skip).limit(size)
        
        result = await self.db.execute(stmt)
        points = result.scalars().all()
        
        return list(points), total
    
    async def update(self, point_id: str, data: Dict[str, Any]) -> Optional[Point]:
        """更新巡检点"""
        point = await self.get_by_id(point_id)
        if not point:
            return None
        
        for key, value in data.items():
            if hasattr(point, key):
                setattr(point, key, value)
        
        await self.db.commit()
        await self.db.refresh(point)
        return point
    
    async def soft_delete(self, point_id: str) -> bool:
        """软删除巡检点"""
        point = await self.get_by_id(point_id)
        if not point:
            return False
        
        point.is_deleted = True
        await self.db.commit()
        return True
    
    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None, point_name: str = None, map_id: str = None) -> Tuple[List[Point], int]:
        """获取所有巡检点列表"""
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size
        
        # 构建查询条件
        conditions = [Point.is_deleted == False]
        
        if point_name:
            conditions.append(Point.point_name.like(f"%{point_name}%"))
        
        if map_id:
            conditions.append(Point.map_id == map_id)
        
        # 查询总数
        count_stmt = select(func.count(Point.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # 查询数据（预加载设备和巡检项目）
        stmt = (
            select(Point)
            .options(
                selectinload(Point.devices).selectinload(Device.items),
                selectinload(Point.devices).selectinload(Device.sensors)
            )
            .where(*conditions)
            .order_by(Point.created_at.desc())
        )
        if skip is not None and limit is not None:
            stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        points = result.scalars().all()
        
        return list(points), total

    async def count_all(self) -> int:
        """统计所有巡检点数量"""
        stmt = select(func.count(Point.id)).where(Point.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def count_by_map(self, map_id: str) -> int:
        """统计地图的巡检点数量"""
        stmt = select(func.count(Point.id)).where(
            Point.map_id == map_id,
            Point.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def check_map_access(self, point_id: str, user_id: str) -> bool:
        """检查用户是否有权限访问巡检点（通过地图权限）"""
        stmt = select(Point).join(Point.map).where(
            Point.id == point_id,
            Point.map.has(user_id=user_id),
            Point.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
