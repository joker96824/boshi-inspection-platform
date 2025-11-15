"""
任务日程数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from ..models.taskschedule import TaskSchedule
from ..models.task import Task
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
        # 重新查询以加载关联数据
        return await self.get_by_id(taskschedule.id) or taskschedule
    
    async def get_by_id(self, taskschedule_id: str) -> Optional[TaskSchedule]:
        """根据ID获取任务日程"""
        stmt = (select(TaskSchedule)
                .options(selectinload(TaskSchedule.task))
                .where(
                    TaskSchedule.id == taskschedule_id,
                    TaskSchedule.is_deleted == False
                ))
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, taskschedule_ids: List[str]) -> List[TaskSchedule]:
        """根据ID列表获取任务日程"""
        query = (select(TaskSchedule)
                .options(selectinload(TaskSchedule.task))
                .where(
                    TaskSchedule.id.in_(taskschedule_ids),
                    TaskSchedule.is_deleted == False
                )
                .order_by(TaskSchedule.created_at.desc()))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: int = 1, size: int = 20, task_id: str = None, 
                       cycle_type: str = None, enabled: bool = None) -> tuple[List[TaskSchedule], int]:
        """获取任务日程列表"""
        # 计算偏移量
        skip = (page - 1) * size
        
        # 构建查询条件
        conditions = [TaskSchedule.is_deleted == False]
        
        if task_id:
            conditions.append(TaskSchedule.task_id == task_id)
        if cycle_type:
            conditions.append(TaskSchedule.cycle_type == cycle_type)
        if enabled is not None:
            conditions.append(TaskSchedule.enabled == enabled)
        
        # 查询总数
        count_stmt = select(func.count(TaskSchedule.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据，按创建时间降序
        stmt = (select(TaskSchedule)
                .options(selectinload(TaskSchedule.task))
                .where(*conditions)
                .order_by(TaskSchedule.created_at.desc())
                .offset(skip)
                .limit(size))
        
        result = await self.db.execute(stmt)
        taskschedules = result.scalars().all()
        
        return list(taskschedules), total
    
    async def get_by_task_id(self, task_id: str, page: int = 1, size: int = 20) -> tuple[List[TaskSchedule], int]:
        """根据任务ID获取任务日程列表"""
        return await self.get_all(page, size, task_id=task_id)
    
    async def update(self, taskschedule_id: str, data: Dict[str, Any]) -> Optional[TaskSchedule]:
        """更新任务日程"""
        taskschedule = await self.get_by_id(taskschedule_id)
        if not taskschedule:
            raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
        
        for key, value in data.items():
            setattr(taskschedule, key, value)
        
        await self.db.commit()
        await self.db.refresh(taskschedule)
        # 重新查询以加载关联数据
        return await self.get_by_id(taskschedule_id)
    
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
        """检查用户是否有权限访问该任务（通过机器人关联）"""
        # 注意：此方法可能需要根据实际权限模型调整
        stmt = select(func.count(Task.id)).join(Task.robot).where(
            Task.id == task_id,
            Task.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0
    
    async def get_all_by_task_id(self, task_id: str) -> List[TaskSchedule]:
        """根据任务ID获取所有任务日程（不分页）"""
        stmt = (select(TaskSchedule)
                .options(selectinload(TaskSchedule.task))
                .where(
                    TaskSchedule.task_id == task_id,
                    TaskSchedule.is_deleted == False
                )
                .order_by(TaskSchedule.created_at.desc()))
        result = await self.db.execute(stmt)
        return list(result.scalars().all())