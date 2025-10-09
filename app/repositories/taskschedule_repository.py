"""
任务日程数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from ..models.taskschedule import TaskSchedule
from ..models.task import Task
from ..models.map import Map
from ..core.exceptions import ResourceNotFoundError


class TaskScheduleRepository:
    """任务日程数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> TaskSchedule:
        """创建任务日程"""
        taskschedule = TaskSchedule(**data)
        self.db.add(taskschedule)
        await self.db.commit()
        await self.db.refresh(taskschedule)
        return taskschedule
    
    async def get_by_id(self, taskschedule_id: str) -> Optional[TaskSchedule]:
        """根据ID获取任务日程"""
        stmt = select(TaskSchedule).where(
            TaskSchedule.id == taskschedule_id,
            TaskSchedule.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_all(self, page: int = 1, size: int = 20, task_id: str = None, 
                       schedule_type: str = None) -> tuple[List[TaskSchedule], int]:
        """获取任务日程列表"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [TaskSchedule.is_deleted == False]
        
        if task_id:
            conditions.append(TaskSchedule.task_id == task_id)
        if schedule_type:
            conditions.append(TaskSchedule.schedule_type.like(f"%{schedule_type}%"))
        
        # 查询总数
        count_stmt = select(func.count(TaskSchedule.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据，按设置时间降序，相同值按创建时间降序
        stmt = (select(TaskSchedule)
                .where(*conditions)
                .order_by(TaskSchedule.set_time.desc(), TaskSchedule.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(stmt)
        taskschedules = result.scalars().all()
        
        return list(taskschedules), total
    
    async def get_by_task_id(self, task_id: str, page: int = 1, size: int = 20,
                            sort_by: str = "set_time", sort_order: str = "desc") -> tuple[List[TaskSchedule], int]:
        """根据任务ID获取任务日程列表"""
        return await self.get_all(page, size, task_id=task_id, sort_by=sort_by, sort_order=sort_order)
    
    async def update(self, taskschedule_id: str, data: Dict[str, Any]) -> Optional[TaskSchedule]:
        """更新任务日程"""
        taskschedule = await self.get_by_id(taskschedule_id)
        if not taskschedule:
            raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
        
        for key, value in data.items():
            setattr(taskschedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(taskschedule)
        return taskschedule
    
    async def soft_delete(self, taskschedule_id: str) -> bool:
        """软删除任务日程"""
        taskschedule = await self.get_by_id(taskschedule_id)
        if not taskschedule:
            raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
        
        taskschedule.is_deleted = True
        await self.db.commit()
        return True
    
    async def count_by_task(self, task_id: str) -> int:
        """统计任务下的日程数量"""
        stmt = select(func.count(TaskSchedule.id)).where(
            TaskSchedule.task_id == task_id,
            TaskSchedule.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def check_task_access(self, task_id: str, user_id: str) -> bool:
        """检查用户是否有权限访问该任务（通过地图权限检查）"""
        stmt = select(func.count(Task.id)).join(Map).where(
            Task.id == task_id,
            Map.user_id == user_id,
            Task.is_deleted == False,
            Map.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
