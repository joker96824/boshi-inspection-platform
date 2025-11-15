"""
云台日程数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import date as date_type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.gimbalschedule import GimbalSchedule
from ..models.gimbaltask import GimbalTask
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
                     cycle_type: str = None, enabled: bool = None,
                     gimbaltask_id: str = None) -> Tuple[List[GimbalSchedule], int]:
        """获取云台日程列表"""
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [GimbalSchedule.is_deleted == False]
        
        if cycle_type:
            conditions.append(GimbalSchedule.cycle_type == cycle_type)
        
        if enabled is not None:
            conditions.append(GimbalSchedule.enabled == enabled)
        
        if gimbaltask_id:
            conditions.append(GimbalSchedule.gimbaltask_id == gimbaltask_id)
        
        # 查询总数
        count_query = select(func.count(GimbalSchedule.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0
        
        # 查询数据
        query = (select(GimbalSchedule)
                .where(and_(*conditions))
                .order_by(GimbalSchedule.created_at.desc())
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
        ).order_by(GimbalSchedule.created_at.desc())
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
            GimbalSchedule.enabled == True
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def get_by_date(self, target_date: date_type, gimbal_ids: Optional[List[str]] = None) -> List[GimbalSchedule]:
        """根据日期获取所有相关的云台日程（可选择按云台ID筛选）"""
        # 构建查询条件
        conditions = [
            GimbalSchedule.is_deleted == False,
            GimbalSchedule.enabled == True,
            GimbalSchedule.start_date <= target_date,
            GimbalSchedule.end_date >= target_date
        ]
        
        # 如果指定了云台ID，通过关联 GimbalTask 来筛选
        if gimbal_ids:
            conditions.append(GimbalTask.gimbal_id.in_(gimbal_ids))
            query = (select(GimbalSchedule)
                    .options(selectinload(GimbalSchedule.gimbal_task))
                    .join(GimbalTask, GimbalSchedule.gimbaltask_id == GimbalTask.id)
                    .where(and_(*conditions))
                    .order_by(GimbalSchedule.created_at.desc()))
        else:
            query = (select(GimbalSchedule)
                    .options(selectinload(GimbalSchedule.gimbal_task))
                    .where(and_(*conditions))
                    .order_by(GimbalSchedule.created_at.desc()))
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
