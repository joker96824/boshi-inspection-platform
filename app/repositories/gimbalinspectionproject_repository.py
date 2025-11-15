"""
云台巡检项目数据仓库
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..core.exceptions import ResourceNotFoundError
from ..models.gimbal import Gimbal
from ..models.gimbalinspectionproject import GimbalInspectionProject
from ..models.gimbaltask import GimbalTask


class GimbalInspectionProjectRepository:
    """云台巡检项目数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> GimbalInspectionProject:
        """创建云台巡检项目"""
        project = GimbalInspectionProject(**data)
        self.db.add(project)
        await self.db.commit()
        await self.db.refresh(project)
        await self.db.refresh(project, attribute_names=["gimbal_task"])
        return project

    async def get_by_id(self, project_id: str) -> Optional[GimbalInspectionProject]:
        """根据ID获取云台巡检项目"""
        query = (
            select(GimbalInspectionProject)
            .options(
                selectinload(GimbalInspectionProject.gimbal_task).selectinload(
                    GimbalTask.gimbal
                ),
                selectinload(GimbalInspectionProject.histories),
            )
            .where(
                GimbalInspectionProject.id == project_id,
                GimbalInspectionProject.is_deleted == False,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(
        self, project_ids: List[str]
    ) -> List[GimbalInspectionProject]:
        """根据ID列表获取云台巡检项目"""
        if not project_ids:
            return []

        query = (
            select(GimbalInspectionProject)
            .options(selectinload(GimbalInspectionProject.gimbal_task))
            .where(
                GimbalInspectionProject.id.in_(project_ids),
                GimbalInspectionProject.is_deleted == False,
            )
            .order_by(
                GimbalInspectionProject.sort_order.asc(),
                GimbalInspectionProject.created_at.desc(),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self,
        page: int = 1,
        size: int = 20,
        task_name: str = None,
        detection_type: str = None,
        gimbaltask_id: str = None,
        gimbal_id: str = None,
        map_id: str = None,
    ) -> Tuple[List[GimbalInspectionProject], int]:
        """获取云台巡检项目列表"""
        skip = (page - 1) * size

        conditions = [GimbalInspectionProject.is_deleted == False]

        if task_name:
            conditions.append(GimbalInspectionProject.task_name.like(f"%{task_name}%"))

        if detection_type:
            conditions.append(
                GimbalInspectionProject.detection_type == detection_type
            )

        if gimbaltask_id:
            conditions.append(GimbalInspectionProject.gimbaltask_id == gimbaltask_id)

        if gimbal_id:
            conditions.append(
                GimbalInspectionProject.gimbal_task.has(GimbalTask.gimbal_id == gimbal_id)
            )

        if map_id:
            conditions.append(
                GimbalInspectionProject.gimbal_task.has(
                    GimbalTask.gimbal.has(Gimbal.map_id == map_id)
                )
            )

        count_query = select(func.count(GimbalInspectionProject.id)).where(
            and_(*conditions)
        )
        total = (await self.db.execute(count_query)).scalar() or 0

        query = (
            select(GimbalInspectionProject)
            .options(selectinload(GimbalInspectionProject.gimbal_task))
            .where(and_(*conditions))
            .order_by(
                GimbalInspectionProject.sort_order.asc(),
                GimbalInspectionProject.created_at.desc(),
            )
            .offset(skip)
            .limit(size)
        )

        result = await self.db.execute(query)
        projects = list(result.scalars().all())

        return projects, total

    async def update(
        self, project_id: str, data: Dict[str, Any]
    ) -> Optional[GimbalInspectionProject]:
        """更新云台巡检项目"""
        project = await self.get_by_id(project_id)
        if not project:
            raise ResourceNotFoundError(f"云台巡检项目ID '{project_id}' 不存在")

        for key, value in data.items():
            setattr(project, key, value)

        await self.db.commit()
        await self.db.refresh(project)
        return project

    async def soft_delete(self, project_id: str, deleted_by: str) -> bool:
        """软删除云台巡检项目"""
        project = await self.get_by_id(project_id)
        if not project:
            return False

        project.is_deleted = True
        project.updated_by = deleted_by
        await self.db.commit()
        return True

    async def exists_by_name(
        self,
        task_name: str,
        gimbaltask_id: str,
        exclude_project_id: str = None,
    ) -> bool:
        """检查同一云台任务下巡检项目名称是否存在"""
        conditions = [
            GimbalInspectionProject.task_name == task_name,
            GimbalInspectionProject.gimbaltask_id == gimbaltask_id,
            GimbalInspectionProject.is_deleted == False,
        ]
        if exclude_project_id:
            conditions.append(GimbalInspectionProject.id != exclude_project_id)

        query = select(GimbalInspectionProject).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def get_by_gimbaltask_id(
        self, gimbaltask_id: str
    ) -> List[GimbalInspectionProject]:
        """根据云台任务ID获取巡检项目列表"""
        query = (
            select(GimbalInspectionProject)
            .where(
                GimbalInspectionProject.gimbaltask_id == gimbaltask_id,
                GimbalInspectionProject.is_deleted == False,
            )
            .order_by(
                GimbalInspectionProject.sort_order.asc(),
                GimbalInspectionProject.created_at.desc(),
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        """统计所有云台巡检项目数量"""
        stmt = select(func.count(GimbalInspectionProject.id)).where(
            GimbalInspectionProject.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def get_next_sort_order(self, gimbaltask_id: str) -> int:
        """获取指定云台任务下下一个排序值"""
        stmt = select(
            func.coalesce(func.max(GimbalInspectionProject.sort_order), -1)
        ).where(
            GimbalInspectionProject.gimbaltask_id == gimbaltask_id,
            GimbalInspectionProject.is_deleted == False,
        )
        result = await self.db.execute(stmt)
        max_sort = result.scalar()
        if max_sort is None:
            return 0
        return max_sort + 1

    async def bulk_update_sort_orders(
        self,
        gimbaltask_id: str,
        sort_orders: List[Dict[str, Any]],
        updated_by: str,
    ) -> None:
        """批量更新同一云台任务下巡检项目的排序"""
        if not sort_orders:
            return

        project_ids = [item["inspection_project_id"] for item in sort_orders]
        sort_mapping = {item["inspection_project_id"]: item["sort_order"] for item in sort_orders}

        query = select(GimbalInspectionProject).where(
            GimbalInspectionProject.id.in_(project_ids),
            GimbalInspectionProject.gimbaltask_id == gimbaltask_id,
            GimbalInspectionProject.is_deleted == False,
        )
        result = await self.db.execute(query)
        projects = list(result.scalars().all())

        if len(projects) != len(project_ids):
            raise ResourceNotFoundError("部分巡检项目不存在或不属于当前云台任务")

        for project in projects:
            project.sort_order = sort_mapping[project.id]
            project.updated_by = updated_by

        await self.db.commit()

