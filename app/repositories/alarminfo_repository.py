"""
报警信息数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

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
        """根据ID获取报警信息"""
        query = select(AlarmInfo).where(
            AlarmInfo.id == alarminfo_id,
            AlarmInfo.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, alarminfo_ids: List[str]) -> List[AlarmInfo]:
        """根据ID列表获取报警信息"""
        query = select(AlarmInfo).where(
            AlarmInfo.id.in_(alarminfo_ids),
            AlarmInfo.is_deleted == False
        ).order_by(AlarmInfo.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, page: int = 1, size: int = 20,
                     alarmrule_id: str = None, itemhistory_id: str = None) -> Tuple[List[AlarmInfo], int]:
        """获取报警信息列表（分页）"""
        skip = (page - 1) * size

        # 构建查询条件
        conditions = [AlarmInfo.is_deleted == False]
        if alarmrule_id:
            conditions.append(AlarmInfo.alarmrule_id == alarmrule_id)
        if itemhistory_id:
            conditions.append(AlarmInfo.itemhistory_id == itemhistory_id)

        # 统计总数
        count_query = select(func.count(AlarmInfo.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (select(AlarmInfo)
                .where(and_(*conditions))
                .order_by(AlarmInfo.created_at.desc())
                .offset(skip)
                .limit(size))
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

