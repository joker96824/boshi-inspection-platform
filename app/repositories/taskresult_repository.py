"""
任务结果数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime

from ..models.taskresult import TaskResult
from ..core.exceptions import ResourceNotFoundError


class TaskResultRepository:
    """任务结果数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> TaskResult:
        """创建任务结果"""
        # 处理时间字符串转换
        if data.get('result_collect_time') and isinstance(data['result_collect_time'], str):
            data['result_collect_time'] = datetime.strptime(data['result_collect_time'], "%Y-%m-%dT%H:%M:%S")
        
        taskresult = TaskResult(**data)
        self.db.add(taskresult)
        await self.db.commit()
        await self.db.refresh(taskresult)
        return taskresult

    async def get_by_id(self, taskresult_id: str) -> Optional[TaskResult]:
        """根据ID获取任务结果"""
        query = select(TaskResult).where(
            TaskResult.id == taskresult_id,
            TaskResult.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, taskresult_ids: List[str]) -> List[TaskResult]:
        """根据ID列表获取任务结果"""
        query = select(TaskResult).where(
            TaskResult.id.in_(taskresult_ids),
            TaskResult.is_deleted == False
        ).order_by(TaskResult.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, page: int = 1, size: int = 20) -> Tuple[List[TaskResult], int]:
        """获取任务结果列表（分页）"""
        skip = (page - 1) * size

        # 统计总数
        count_query = select(func.count(TaskResult.id)).where(TaskResult.is_deleted == False)
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (select(TaskResult)
                .where(TaskResult.is_deleted == False)
                .order_by(TaskResult.created_at.desc())
                .offset(skip)
                .limit(size))
        result = await self.db.execute(query)
        taskresults = list(result.scalars().all())

        return taskresults, total

    async def get_by_taskhistory_id(self, taskhistory_id: str) -> Optional[TaskResult]:
        """根据任务记录ID获取任务结果（1对1关系）"""
        query = select(TaskResult).where(
            TaskResult.taskhistory_id == taskhistory_id,
            TaskResult.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, taskresult_id: str, data: Dict[str, Any]) -> Optional[TaskResult]:
        """更新任务结果"""
        taskresult = await self.get_by_id(taskresult_id)
        if not taskresult:
            raise ResourceNotFoundError(f"任务结果ID '{taskresult_id}' 不存在")

        # 处理时间字符串转换
        if data.get('result_collect_time') and isinstance(data['result_collect_time'], str):
            data['result_collect_time'] = datetime.strptime(data['result_collect_time'], "%Y-%m-%dT%H:%M:%S")

        for key, value in data.items():
            setattr(taskresult, key, value)

        await self.db.commit()
        await self.db.refresh(taskresult)
        return taskresult

    async def delete(self, taskresult_id: str) -> bool:
        """删除任务结果（软删除）"""
        taskresult = await self.get_by_id(taskresult_id)
        if not taskresult:
            raise ResourceNotFoundError(f"任务结果ID '{taskresult_id}' 不存在")

        taskresult.is_deleted = True
        await self.db.commit()
        return True

    async def exists_by_taskhistory_id(self, taskhistory_id: str, exclude_id: str = None) -> bool:
        """检查任务记录是否已有结果（1对1关系校验）"""
        conditions = [
            TaskResult.taskhistory_id == taskhistory_id,
            TaskResult.is_deleted == False
        ]
        if exclude_id:
            conditions.append(TaskResult.id != exclude_id)
        
        query = select(TaskResult).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_all(self) -> int:
        """统计所有任务结果数量"""
        stmt = select(func.count(TaskResult.id)).where(TaskResult.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
