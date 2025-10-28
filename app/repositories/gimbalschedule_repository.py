"""
云台日程数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.gimbalschedule import GimbalSchedule
from ..core.exceptions import ResourceNotFoundError


class GimbalScheduleRepository:
    """云台日程数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> GimbalSchedule:
        """创建云台日程"""
        schedule = GimbalSchedule(**data)
        self.db.add(schedule)
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def get_by_id(self, schedule_id: str) -> Optional[GimbalSchedule]:
        """根据ID获取云台日程"""
        query = select(GimbalSchedule).where(
            GimbalSchedule.id == schedule_id,
            GimbalSchedule.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, schedule_ids: List[str]) -> List[GimbalSchedule]:
        """根据ID列表获取云台日程"""
        if not schedule_ids:
            return []
        
        query = select(GimbalSchedule).where(
            GimbalSchedule.id.in_(schedule_ids),
            GimbalSchedule.is_deleted == False
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20,
                     schedule_type: str = None, schedule_is_active: bool = None,
                     gimbaltask_id: str = None) -> Tuple[List[GimbalSchedule], int]:
        """获取云台日程列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [GimbalSchedule.is_deleted == False]
        
        if schedule_type:
            conditions.append(GimbalSchedule.schedule_type == schedule_type)
        
        if schedule_is_active is not None:
            conditions.append(GimbalSchedule.schedule_is_active == schedule_is_active)
        
        if gimbaltask_id:
            conditions.append(GimbalSchedule.gimbaltask_id == gimbaltask_id)
        
        # 查询总数
        count_query = select(func.count(GimbalSchedule.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(GimbalSchedule)
                .where(and_(*conditions))
                .order_by(GimbalSchedule.set_time.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(query)
        schedules = list(result.scalars().all())
        
        return schedules, total
    
    async def update(self, schedule_id: str, data: Dict[str, Any]) -> Optional[GimbalSchedule]:
        """更新云台日程"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            raise ResourceNotFoundError(f"云台日程ID '{schedule_id}' 不存在")
        
        for key, value in data.items():
            setattr(schedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(schedule)
        return schedule
    
    async def soft_delete(self, schedule_id: str, deleted_by: str) -> bool:
        """软删除云台日程"""
        schedule = await self.get_by_id(schedule_id)
        if not schedule:
            return False
        
        schedule.is_deleted = True
        schedule.updated_by = deleted_by
        await self.db.commit()
        return True
    
    async def get_by_gimbaltask_id(self, gimbaltask_id: str) -> List[GimbalSchedule]:
        """根据云台任务ID获取所有云台日程"""
        query = select(GimbalSchedule).where(
            GimbalSchedule.gimbaltask_id == gimbaltask_id,
            GimbalSchedule.is_deleted == False
        ).order_by(GimbalSchedule.set_time.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all(self) -> int:
        """统计所有云台日程数量"""
        stmt = select(func.count(GimbalSchedule.id)).where(GimbalSchedule.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def count_active(self) -> int:
        """统计激活的云台日程数量"""
        stmt = select(func.count(GimbalSchedule.id)).where(
            GimbalSchedule.is_deleted == False,
            GimbalSchedule.schedule_is_active == True
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
