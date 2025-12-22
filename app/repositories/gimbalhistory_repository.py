"""
云台巡检记录数据仓库
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.exceptions import ResourceNotFoundError
from ..models.gimbalhistory import GimbalHistory


class GimbalHistoryRepository:
    """云台巡检记录数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> GimbalHistory:
        """创建云台巡检记录"""
        history = GimbalHistory(**data)
        self.db.add(history)
        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def get_by_id(self, history_id: str) -> Optional[GimbalHistory]:
        """根据ID获取云台巡检记录（预加载关联信息）"""
        from sqlalchemy.orm import selectinload
        from ..models.gimbalinspectionprojectpresetpoint import GimbalInspectionProjectPresetPoint
        
        query = (
            select(GimbalHistory)
            .options(
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.inspection_project),
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .where(
                GimbalHistory.id == history_id, 
                GimbalHistory.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, history_ids: List[str]) -> List[GimbalHistory]:
        """根据ID列表获取云台巡检记录（预加载关联信息）"""
        if not history_ids:
            return []

        from sqlalchemy.orm import selectinload
        from ..models.gimbalinspectionprojectpresetpoint import GimbalInspectionProjectPresetPoint

        query = (
            select(GimbalHistory)
            .options(
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.inspection_project),
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .where(
                GimbalHistory.id.in_(history_ids), 
                GimbalHistory.is_deleted == False
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(
        self, page: Optional[int] = None, size: Optional[int] = None, 
        project_preset_point_id: str = None, inspection_project_id: str = None,
        view_status: str = None, inspection_result_status: str = None
    ) -> Tuple[List[GimbalHistory], int]:
        """获取云台巡检记录列表"""
        # 导入必要的模型（必须在函数开头导入，因为后面会用到）
        from sqlalchemy.orm import selectinload
        from ..models.gimbalinspectionprojectpresetpoint import GimbalInspectionProjectPresetPoint
        
        # 如果未提供分页参数，返回所有数据
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size

        conditions = [GimbalHistory.is_deleted == False]

        if project_preset_point_id:
            conditions.append(
                GimbalHistory.project_preset_point_id == project_preset_point_id
            )
        
        if inspection_project_id:
            # 通过中间表关联查询
            conditions.append(
                GimbalHistory.project_preset_point.has(
                    GimbalInspectionProjectPresetPoint.inspection_project_id == inspection_project_id
                )
            )
        
        if view_status:
            conditions.append(GimbalHistory.view_status == view_status)
        
        if inspection_result_status:
            conditions.append(GimbalHistory.inspection_result_status == inspection_result_status)

        count_query = select(func.count(GimbalHistory.id)).where(and_(*conditions))
        total = (await self.db.execute(count_query)).scalar() or 0
        
        query = (
            select(GimbalHistory)
            .options(
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.inspection_project),
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .where(and_(*conditions))
            .order_by(GimbalHistory.created_at.desc())
        )
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        histories = list(result.scalars().all())

        return histories, total

    async def update(
        self, history_id: str, data: Dict[str, Any]
    ) -> Optional[GimbalHistory]:
        """更新云台巡检记录"""
        history = await self.get_by_id(history_id)
        if not history:
            raise ResourceNotFoundError(f"云台记录ID '{history_id}' 不存在")

        for key, value in data.items():
            setattr(history, key, value)

        await self.db.commit()
        await self.db.refresh(history)
        return history

    async def soft_delete(self, history_id: str, deleted_by: str) -> bool:
        """软删除云台巡检记录"""
        history = await self.get_by_id(history_id)
        if not history:
            return False

        history.is_deleted = True
        history.updated_by = deleted_by
        await self.db.commit()
        return True

    async def get_by_inspection_project_id(
        self, inspection_project_id: str
    ) -> List[GimbalHistory]:
        """根据巡检项目ID获取云台巡检记录（通过中间表关联）"""
        from sqlalchemy.orm import selectinload
        from ..models.gimbalinspectionprojectpresetpoint import GimbalInspectionProjectPresetPoint
        
        query = (
            select(GimbalHistory)
            .options(
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.inspection_project),
                selectinload(GimbalHistory.project_preset_point)
                .selectinload(GimbalInspectionProjectPresetPoint.preset_point),
            )
            .join(
                GimbalInspectionProjectPresetPoint,
                GimbalHistory.project_preset_point_id == GimbalInspectionProjectPresetPoint.id
            )
            .where(
                GimbalInspectionProjectPresetPoint.inspection_project_id == inspection_project_id,
                GimbalHistory.is_deleted == False,
            )
            .order_by(GimbalHistory.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def count_all(self) -> int:
        """统计所有云台巡检记录数量"""
        stmt = select(func.count(GimbalHistory.id)).where(
            GimbalHistory.is_deleted == False
        )
        result = await self.db.execute(stmt)
        return result.scalar() or 0

