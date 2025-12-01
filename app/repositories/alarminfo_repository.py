"""
报警信息数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
import json

from ..models.alarminfo import AlarmInfo
from ..core.exceptions import ResourceNotFoundError


class AlarmInfoRepository:
    """报警信息数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> AlarmInfo:
        """创建报警信息"""
        alarminfo = AlarmInfo(**data)
        self.db.add(alarminfo)
        await self.db.commit()
        await self.db.refresh(alarminfo)
        return alarminfo

    async def get_by_id(self, alarminfo_id: str) -> Optional[AlarmInfo]:
        """根据ID获取报警信息（预加载报警规则）"""
        query = (
            select(AlarmInfo)
            .options(selectinload(AlarmInfo.alarm_rule))
            .where(AlarmInfo.id == alarminfo_id, AlarmInfo.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, alarminfo_ids: List[str]) -> List[AlarmInfo]:
        """根据ID列表获取报警信息"""
        if not alarminfo_ids:
            return []

        query = (
            select(AlarmInfo)
            .options(selectinload(AlarmInfo.alarm_rule))
            .where(
                AlarmInfo.id.in_(alarminfo_ids),
                AlarmInfo.is_deleted == False
            )
            .order_by(AlarmInfo.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None,
                     alarm_rule_id: str = None, alarm_category: str = None,
                     alarm_level: int = None, alarm_status: str = None,
                     source_type: str = None, relation_type: str = None,
                     relation_id: str = None, trigger_item_id: str = None,
                     trigger_project_id: str = None) -> Tuple[List[AlarmInfo], int]:
        """获取报警信息列表（分页）"""
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size

        # 构建查询条件
        conditions = [AlarmInfo.is_deleted == False]

        if alarm_rule_id:
            conditions.append(AlarmInfo.alarm_rule_id == alarm_rule_id)
        if alarm_category:
            conditions.append(AlarmInfo.alarm_category == alarm_category)
        if alarm_level is not None:
            conditions.append(AlarmInfo.alarm_level == alarm_level)
        if alarm_status:
            conditions.append(AlarmInfo.alarm_status == alarm_status)
        if source_type:
            conditions.append(AlarmInfo.source_type == source_type)
        if relation_type:
            conditions.append(AlarmInfo.relation_type == relation_type)
        if relation_id:
            # JSON字段查询：relation_ids包含relation_id
            conditions.append(
                func.JSON_CONTAINS(AlarmInfo.relation_ids, json.dumps(relation_id))
            )
        if trigger_item_id:
            # JSON字段查询：trigger_item_ids包含trigger_item_id
            conditions.append(
                func.JSON_CONTAINS(AlarmInfo.trigger_item_ids, json.dumps(trigger_item_id))
            )
        if trigger_project_id:
            # JSON字段查询：trigger_project_ids包含trigger_project_id
            conditions.append(
                func.JSON_CONTAINS(AlarmInfo.trigger_project_ids, json.dumps(trigger_project_id))
            )

        # 统计总数
        count_query = select(func.count(AlarmInfo.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (
            select(AlarmInfo)
            .options(selectinload(AlarmInfo.alarm_rule))
            .where(and_(*conditions))
            .order_by(AlarmInfo.created_at.desc(), AlarmInfo.id.desc())
        )
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        alarminfos = list(result.scalars().all())

        return alarminfos, total

    async def update(self, alarminfo_id: str, data: Dict[str, Any]) -> Optional[AlarmInfo]:
        """更新报警信息"""
        alarminfo = await self.get_by_id(alarminfo_id)
        if not alarminfo:
            raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

        for key, value in data.items():
            setattr(alarminfo, key, value)

        await self.db.commit()
        await self.db.refresh(alarminfo)
        return alarminfo

    async def delete(self, alarminfo_id: str) -> bool:
        """删除报警信息（软删除）"""
        alarminfo = await self.get_by_id(alarminfo_id)
        if not alarminfo:
            raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

        alarminfo.is_deleted = True
        await self.db.commit()
        return True

    async def count_all(self) -> int:
        """统计所有报警信息数量"""
        stmt = select(func.count(AlarmInfo.id)).where(AlarmInfo.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

    async def exists_by_rule_and_source_ids(self, alarm_rule_id: str, source_ids: List[str]) -> Optional[AlarmInfo]:
        """
        检查是否存在相同的报警信息（去重逻辑）
        同一个报警规则id，同一组source_ids只能有一个报警信息
        """
        # 对source_ids进行排序，确保顺序一致
        sorted_source_ids = sorted(source_ids)
        source_ids_json = json.dumps(sorted_source_ids)

        # 查询是否存在相同的报警信息
        # 使用JSON_CONTAINS或JSON_SEARCH来匹配
        query = (
            select(AlarmInfo)
            .where(
                AlarmInfo.alarm_rule_id == alarm_rule_id,
                AlarmInfo.is_deleted == False,
                # 使用JSON长度和内容匹配
                func.JSON_LENGTH(AlarmInfo.source_ids) == len(sorted_source_ids)
            )
        )
        result = await self.db.execute(query)
        alarminfos = list(result.scalars().all())

        # 在Python中比较JSON内容（因为MySQL的JSON比较可能不够精确）
        for alarminfo in alarminfos:
            if alarminfo.source_ids:
                existing_ids = sorted(alarminfo.source_ids) if isinstance(alarminfo.source_ids, list) else sorted(json.loads(alarminfo.source_ids))
                if existing_ids == sorted_source_ids:
                    return alarminfo

        return None
