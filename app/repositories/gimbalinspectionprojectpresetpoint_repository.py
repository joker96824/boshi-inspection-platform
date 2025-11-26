"""
云台巡检项目-预设点关联数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload

from ..models.gimbalinspectionprojectpresetpoint import (
    GimbalInspectionProjectPresetPoint,
)
from ..core.exceptions import ResourceNotFoundError


class GimbalInspectionProjectPresetPointRepository:
    """云台巡检项目-预设点关联数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> GimbalInspectionProjectPresetPoint:
        """创建关联"""
        link = GimbalInspectionProjectPresetPoint(**data)
        self.db.add(link)
        await self.db.commit()
        await self.db.refresh(link)
        return link

    async def create_batch(
        self, links_data: List[Dict[str, Any]]
    ) -> List[GimbalInspectionProjectPresetPoint]:
        """批量创建关联"""
        links = [
            GimbalInspectionProjectPresetPoint(**link_data) for link_data in links_data
        ]
        self.db.add_all(links)
        await self.db.commit()
        for link in links:
            await self.db.refresh(link)
        return links

    async def get_by_id(self, link_id: str) -> Optional[GimbalInspectionProjectPresetPoint]:
        """根据ID获取关联"""
        query = (
            select(GimbalInspectionProjectPresetPoint)
            .options(
                selectinload(GimbalInspectionProjectPresetPoint.inspection_project),
                selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .where(
                GimbalInspectionProjectPresetPoint.id == link_id,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_inspection_project_id(
        self, inspection_project_id: str
    ) -> List[GimbalInspectionProjectPresetPoint]:
        """根据巡检项目ID获取所有关联"""
        query = (
            select(GimbalInspectionProjectPresetPoint)
            .options(
                selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .where(
                GimbalInspectionProjectPresetPoint.inspection_project_id
                == inspection_project_id,
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def find_existing_link(
        self,
        inspection_project_id: str,
        preset_point_id: str,
        detection_type: str,
    ) -> Optional[GimbalInspectionProjectPresetPoint]:
        """查找已存在的关联"""
        query = (
            select(GimbalInspectionProjectPresetPoint)
            .where(
                GimbalInspectionProjectPresetPoint.inspection_project_id
                == inspection_project_id,
                GimbalInspectionProjectPresetPoint.preset_point_id == preset_point_id,
                GimbalInspectionProjectPresetPoint.detection_type == detection_type,
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_inspection_project_id(
        self, inspection_project_id: str
    ) -> int:
        """根据巡检项目ID删除所有关联（物理删除）"""
        stmt = delete(GimbalInspectionProjectPresetPoint).where(
            GimbalInspectionProjectPresetPoint.inspection_project_id == inspection_project_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount

    async def delete_by_id(self, link_id: str) -> bool:
        """删除关联（物理删除）"""
        stmt = delete(GimbalInspectionProjectPresetPoint).where(
            GimbalInspectionProjectPresetPoint.id == link_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

