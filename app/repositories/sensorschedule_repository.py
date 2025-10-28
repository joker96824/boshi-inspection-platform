"""
传感器日程数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.sensorschedule import SensorSchedule
from ..core.exceptions import ResourceNotFoundError


class SensorScheduleRepository:
    """传感器日程数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> SensorSchedule:
        """创建传感器日程"""
        schedule = SensorSchedule(**data)
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def get_by_id(self, schedule_id: str) -> Optional[SensorSchedule]:
        """根据ID获取传感器日程"""
        query = select(SensorSchedule).where(
            SensorSchedule.id == schedule_id,
            SensorSchedule.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, schedule_ids: List[str]) -> List[SensorSchedule]:
        """根据ID列表获取传感器日程"""
        if not schedule_ids:
            return []
        
        query = select(SensorSchedule).where(
            SensorSchedule.id.in_(schedule_ids),
            SensorSchedule.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20,
                     schedule_type: str = None, schedule_is_active: bool = None,
                     sensor_id: str = None) -> Tuple[List[SensorSchedule], int]:
        """获取传感器日程列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [SensorSchedule.is_deleted == False]
        
        if schedule_type:
            conditions.append(SensorSchedule.schedule_type == schedule_type)
        
        if schedule_is_active is not None:
            conditions.append(SensorSchedule.schedule_is_active == schedule_is_active)
        
        if sensor_id:
            conditions.append(SensorSchedule.sensor_id == sensor_id)
        
        # 查询总数
        count_query = select(func.count(SensorSchedule.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(SensorSchedule)
                .where(and_(*conditions))
                .order_by(SensorSchedule.set_time.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        schedules = list(result.scalars().all())
        
        return schedules, total
    
    async def update(self, schedule_id: str, data: Dict[str, Any]) -> Optional[SensorSchedule]:
        """更新传感器日程"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise ResourceNotFoundError(f"传感器日程ID '{schedule_id}' 不存在")
        
        for key, value in data.items():
            setattr(schedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def soft_delete(self, schedule_id: str, deleted_by: str) -> bool:
        """软删除传感器日程"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return False
        
        schedule.is_deleted = True
        schedule.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def get_by_sensor_id(self, sensor_id: str) -> List[SensorSchedule]:
        """根据传感器ID获取所有传感器日程"""
        query = select(SensorSchedule).where(
            SensorSchedule.sensor_id == sensor_id,
            SensorSchedule.is_deleted == False
        ).order_by(SensorSchedule.set_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self) -> int:
        """统计所有传感器日程数量"""
        stmt = select(func.count(SensorSchedule.id)).where(SensorSchedule.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_active(self) -> int:
        """统计激活的传感器日程数量"""
        stmt = select(func.count(SensorSchedule.id)).where(
            SensorSchedule.is_deleted == False,
            SensorSchedule.schedule_is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
