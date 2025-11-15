"""
云台任务数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import ResourceNotFoundError
from ..models.gimbal import Gimbal
from ..models.gimbaltask import GimbalTask


class GimbalTaskRepository:
    """云台任务数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> GimbalTask:
        """创建云台任务"""
        gimbal_task = GimbalTask(**data)
        self.db.add(gimbal_task)
        await self.db.commit()
        await self.db.refresh(gimbal_task)
        await self.db.refresh(
            gimbal_task, attribute_names=["gimbal", "inspection_projects", "schedules"]
        )
        return gimbal_task

    async def get_by_id(self, task_id: str) -> Optional[GimbalTask]:
        """根据ID获取云台任务"""
        query = (
            select(GimbalTask)
            .options(
                selectinload(GimbalTask.gimbal),
                selectinload(GimbalTask.inspection_projects),
                selectinload(GimbalTask.schedules),
            )
            .where(GimbalTask.id == task_id, GimbalTask.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, task_ids: List[str]) -> List[GimbalTask]:
        """根据ID列表获取云台任务"""
        if not task_ids:
            return []

        query = (
            select(GimbalTask)
            .options(
                selectinload(GimbalTask.gimbal),
                selectinload(GimbalTask.inspection_projects),
                selectinload(GimbalTask.schedules),
            )
            .where(GimbalTask.id.in_(task_ids), GimbalTask.is_deleted == False)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        task_name: str = None,
        gimbal_id: str = None,
        map_id: str = None,
    ) -> Tuple[List[GimbalTask], int]:
        """获取云台任务列表"""
        skip = (page - 1) * size

        conditions = [GimbalTask.is_deleted == False]

        if task_name:
            conditions.append(GimbalTask.task_name.like(f"%{task_name}%"))

        if gimbal_id:
            conditions.append(GimbalTask.gimbal_id == gimbal_id)

        if map_id:
            conditions.append(GimbalTask.gimbal.has(Gimbal.map_id == map_id))

        count_query = select(func.count(GimbalTask.id)).where(and_(*conditions))
        total = (await self.db.execute(count_query)).scalar() or 0

        query = (
            select(GimbalTask)
            .options(
                selectinload(GimbalTask.gimbal),
                selectinload(GimbalTask.inspection_projects),
                selectinload(GimbalTask.schedules),
            )
            .where(and_(*conditions))
            .order_by(GimbalTask.created_at.desc())
            .offset(skip)
            .limit(size)
        )

        result = await self.db.execute(query)
        tasks = list(result.scalars().all())

        return tasks, total

    async def update(self, task_id: str, data: Dict[str, Any]) -> Optional[GimbalTask]:
        """更新云台任务"""
        task = await self.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")

        for key, value in data.items():
            setattr(task, key, value)

        await self.db.commit()
        await self.db.refresh(task)
        return task

    async def soft_delete(self, task_id: str, deleted_by: str) -> bool:
        """软删除云台任务"""
        task = await self.get_by_id(task_id)
        if not task:
            return False

        task.is_deleted = True
        task.updated_by = deleted_by
        await self.db.commit()
        return True

    async def exists_by_name(self, task_name: str, exclude_task_id: str = None) -> bool:
        """检查云台任务名是否已存在"""
        conditions = [
            GimbalTask.task_name == task_name,
            GimbalTask.is_deleted == False,
        ]
        if exclude_task_id:
            conditions.append(GimbalTask.id != exclude_task_id)

        query = select(GimbalTask).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_by_gimbal_id(self, gimbal_id: str) -> List[GimbalTask]:
        """根据云台ID获取所有云台任务"""
        query = (
            select(GimbalTask)
            .options(
                selectinload(GimbalTask.inspection_projects),
                selectinload(GimbalTask.schedules),
            )
            .where(GimbalTask.gimbal_id == gimbal_id, GimbalTask.is_deleted == False)
            .order_by(GimbalTask.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        """统计所有云台任务数量"""
        stmt = select(func.count(GimbalTask.id)).where(GimbalTask.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0
