"""
超声波状态配置数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.ultrasonic import Ultrasonic
from ..core.exceptions import ResourceNotFoundError


class UltrasonicRepository:
    """超声波状态配置数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> Ultrasonic:
        """创建超声波状态配置"""
        ultrasonic = Ultrasonic(**data)
        self.db.add(ultrasonic)
        await self.db.commit()
        await self.db.refresh(ultrasonic)
        return ultrasonic

    async def get_by_id(self, ultrasonic_id: str) -> Optional[Ultrasonic]:
        """根据ID获取超声波状态配置"""
        stmt = select(Ultrasonic).where(
            Ultrasonic.id == ultrasonic_id,
            Ultrasonic.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, page: int = 1, size: int = 20, 
                      ultrasonic_id: int = None, baud_rate: int = None,
                      obstacle_avoidance_distance_min: float = None,
                      obstacle_avoidance_distance_max: float = None) -> Tuple[List[Ultrasonic], int]:
        """获取超声波状态配置列表"""
        skip = (page - 1) * size
        conditions = [Ultrasonic.is_deleted == False]
        
        if ultrasonic_id is not None:
            conditions.append(Ultrasonic.ultrasonic_id == ultrasonic_id)
        if baud_rate is not None:
            conditions.append(Ultrasonic.baud_rate == baud_rate)
        if obstacle_avoidance_distance_min is not None:
            conditions.append(Ultrasonic.obstacle_avoidance_distance >= obstacle_avoidance_distance_min)
        if obstacle_avoidance_distance_max is not None:
            conditions.append(Ultrasonic.obstacle_avoidance_distance <= obstacle_avoidance_distance_max)
        
        # 查询总数
        count_query = select(func.count(Ultrasonic.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(Ultrasonic)
                .where(and_(*conditions))
                .order_by(Ultrasonic.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        ultrasonics = list(result.scalars().all())
        return ultrasonics, total

    async def get_by_ids(self, ultrasonic_ids: List[str]) -> List[Ultrasonic]:
        """根据ID列表获取超声波状态配置"""
        stmt = select(Ultrasonic).where(
            Ultrasonic.id.in_(ultrasonic_ids),
            Ultrasonic.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(self, ultrasonic_id: str, data: Dict[str, Any]) -> Optional[Ultrasonic]:
        """更新超声波状态配置"""
        stmt = select(Ultrasonic).where(
            Ultrasonic.id == ultrasonic_id,
            Ultrasonic.is_deleted == False
        )
        result = await self.db.execute(stmt)
        ultrasonic = result.scalar_one_or_none()
        
        if not ultrasonic:
            return None
        
        for key, value in data.items():
            if hasattr(ultrasonic, key):
                setattr(ultrasonic, key, value)
        
        await self.db.commit()
        await self.db.refresh(ultrasonic)
        return ultrasonic

    async def soft_delete(self, ultrasonic_id: str, updated_by: str) -> bool:
        """软删除超声波状态配置"""
        stmt = select(Ultrasonic).where(
            Ultrasonic.id == ultrasonic_id,
            Ultrasonic.is_deleted == False
        )
        result = await self.db.execute(stmt)
        ultrasonic = result.scalar_one_or_none()
        
        if not ultrasonic:
            return False
        
        ultrasonic.is_deleted = True
        ultrasonic.updated_by = updated_by
        await self.db.commit()
        return True

    async def get_stats(self) -> Dict[str, Any]:
        """获取超声波状态配置统计信息"""
        # 总数统计
        total_stmt = select(func.count(Ultrasonic.id)).where(Ultrasonic.is_deleted == False)
        total_result = await self.db.execute(total_stmt)
        total = total_result.scalar() or 0
        
        # 按超声波ID统计
        id_stmt = select(
            Ultrasonic.ultrasonic_id,
            func.count(Ultrasonic.id).label('count')
        ).where(Ultrasonic.is_deleted == False).group_by(Ultrasonic.ultrasonic_id)
        id_result = await self.db.execute(id_stmt)
        id_stats = {row.ultrasonic_id: row.count for row in id_result}
        
        # 按波特率统计
        baud_stmt = select(
            Ultrasonic.baud_rate,
            func.count(Ultrasonic.id).label('count')
        ).where(Ultrasonic.is_deleted == False).group_by(Ultrasonic.baud_rate)
        baud_result = await self.db.execute(baud_stmt)
        baud_stats = {row.baud_rate: row.count for row in baud_result}
        
        # 距离统计
        distance_stats_stmt = select(
            func.avg(Ultrasonic.obstacle_avoidance_distance).label('avg_obstacle_distance'),
            func.min(Ultrasonic.obstacle_avoidance_distance).label('min_obstacle_distance'),
            func.max(Ultrasonic.obstacle_avoidance_distance).label('max_obstacle_distance'),
            func.avg(Ultrasonic.deceleration_distance).label('avg_deceleration_distance'),
            func.min(Ultrasonic.deceleration_distance).label('min_deceleration_distance'),
            func.max(Ultrasonic.deceleration_distance).label('max_deceleration_distance')
        ).where(Ultrasonic.is_deleted == False)
        distance_result = await self.db.execute(distance_stats_stmt)
        distance_stats = distance_result.first()
        
        return {
            "total": total,
            "id_stats": id_stats,
            "baud_stats": baud_stats,
            "distance_stats": {
                "avg_obstacle_distance": float(distance_stats.avg_obstacle_distance) if distance_stats.avg_obstacle_distance else 0,
                "min_obstacle_distance": float(distance_stats.min_obstacle_distance) if distance_stats.min_obstacle_distance else 0,
                "max_obstacle_distance": float(distance_stats.max_obstacle_distance) if distance_stats.max_obstacle_distance else 0,
                "avg_deceleration_distance": float(distance_stats.avg_deceleration_distance) if distance_stats.avg_deceleration_distance else 0,
                "min_deceleration_distance": float(distance_stats.min_deceleration_distance) if distance_stats.min_deceleration_distance else 0,
                "max_deceleration_distance": float(distance_stats.max_deceleration_distance) if distance_stats.max_deceleration_distance else 0
            }
        }
