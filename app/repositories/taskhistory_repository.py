"""
任务记录数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..models.taskhistory import TaskHistory
from ..models.task import Task
from ..models.map import Map
from ..core.exceptions import ResourceNotFoundError


class TaskHistoryRepository:
    """任务记录数据仓库"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: Dict[str, Any]) -> TaskHistory:
        """创建任务记录"""
        taskhistory = TaskHistory(**data)
        self.db.add(taskhistory)
        await self.db.commit()
        await self.db.refresh(taskhistory)
        return taskhistory
    
    async def get_by_id(self, taskhistory_id: str) -> Optional[TaskHistory]:
        """根据ID获取任务记录"""
        stmt = select(TaskHistory).where(
            TaskHistory.id == taskhistory_id,
            TaskHistory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_ids(self, taskhistory_ids: List[str]) -> List[TaskHistory]:
        """根据ID列表获取任务记录"""
        query = select(TaskHistory).where(
            TaskHistory.id.in_(taskhistory_ids),
            TaskHistory.is_deleted == False
        ).order_by(TaskHistory.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None, 
                      task_id: str = None, record_status: str = None, record_batch: int = None,
                      start_time_from: str = None, start_time_to: str = None,
                      end_time_from: str = None, end_time_to: str = None) -> tuple[List[TaskHistory], int]:
        """获取任务记录列表"""
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            # 计算偏移量
            skip = (page - 1) * size
            limit = size
        
        # 构建查询条件
        conditions = [TaskHistory.is_deleted == False]
        
        if task_id:
            conditions.append(TaskHistory.task_id == task_id)
        if record_status:
            conditions.append(TaskHistory.record_status == record_status)
        if record_batch:
            conditions.append(TaskHistory.record_batch == record_batch)
        if start_time_from:
            from datetime import datetime
            start_from_dt = datetime.strptime(start_time_from, "%Y-%m-%dT%H:%M:%S")
            conditions.append(TaskHistory.record_start_time >= start_from_dt)
        if start_time_to:
            from datetime import datetime
            start_to_dt = datetime.strptime(start_time_to, "%Y-%m-%dT%H:%M:%S")
            conditions.append(TaskHistory.record_start_time <= start_to_dt)
        if end_time_from:
            from datetime import datetime
            end_from_dt = datetime.strptime(end_time_from, "%Y-%m-%dT%H:%M:%S")
            conditions.append(TaskHistory.record_end_time >= end_from_dt)
        if end_time_to:
            from datetime import datetime
            end_to_dt = datetime.strptime(end_time_to, "%Y-%m-%dT%H:%M:%S")
            conditions.append(TaskHistory.record_end_time <= end_to_dt)
        
        # 查询总数
        count_stmt = select(func.count(TaskHistory.id)).where(*conditions)
        count_result = await self.db.execute(count_stmt)
        total = count_result.scalar()
        
        # 查询数据，按创建时间降序
        stmt = (select(TaskHistory)
                .where(*conditions)
                .order_by(TaskHistory.created_at.desc()))
        if skip is not None and limit is not None:
            stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        taskhistories = result.scalars().all()
        
        return list(taskhistories), total
    
    async def get_by_task_id(self, task_id: str, page: int = 1, size: int = 20) -> tuple[List[TaskHistory], int]:
        """根据任务ID获取任务记录列表"""
        return await self.get_all(page, size, task_id=task_id)
    
    async def update(self, taskhistory_id: str, data: Dict[str, Any]) -> Optional[TaskHistory]:
        """更新任务记录"""
        taskhistory = await self.get_by_id(taskhistory_id)
        if not taskhistory:
            raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
        
        for key, value in data.items():
            setattr(taskhistory, key, value)
        
        await self.db.commit()
        await self.db.refresh(taskhistory)
        return taskhistory
    
    async def soft_delete(self, taskhistory_id: str) -> bool:
        """软删除任务记录"""
        taskhistory = await self.get_by_id(taskhistory_id)
        if not taskhistory:
            raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
        
        taskhistory.is_deleted = True
        await self.db.commit()
        return True
    
    async def count_by_task_id(self, task_id: str) -> int:
        """统计任务下的记录数量"""
        stmt = select(func.count(TaskHistory.id)).where(
            TaskHistory.task_id == task_id,
            TaskHistory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one()
    
    async def check_task_access(self, task_id: str, user_id: str) -> bool:
        """检查用户是否有权限访问该任务记录所属的任务（通过地图权限检查）"""
        stmt = select(func.count(Task.id)).join(Map).where(
            Task.id == task_id,
            Map.user_id == user_id,
            Task.is_deleted == False,
            Map.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar_one() > 0