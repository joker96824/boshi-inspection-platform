"""
报警规则数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_

from ..models.alarmrule import AlarmRule
from ..core.exceptions import ResourceNotFoundError


class AlarmRuleRepository:
    """报警规则数据仓库"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> AlarmRule:
        """创建报警规则"""
        alarmrule = AlarmRule(**data)
        self.db.add(alarmrule)
        await self.db.commit()
        await self.db.refresh(alarmrule)
        return alarmrule

    async def get_by_id(self, alarmrule_id: str) -> Optional[AlarmRule]:
        """根据ID获取报警规则"""
        query = select(AlarmRule).where(
            AlarmRule.id == alarmrule_id,
            AlarmRule.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, alarmrule_ids: List[str]) -> List[AlarmRule]:
        """根据ID列表获取报警规则"""
        query = select(AlarmRule).where(
            AlarmRule.id.in_(alarmrule_ids),
            AlarmRule.is_deleted == False
        ).order_by(AlarmRule.created_at.desc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, page: int = 1, size: int = 20,
                     rule_name: str = None, item_id: str = None) -> Tuple[List[AlarmRule], int]:
        """获取报警规则列表（分页）"""
        skip = (page - 1) * size

        # 构建查询条件
        conditions = [AlarmRule.is_deleted == False]
        if rule_name:
            conditions.append(AlarmRule.rule_name.like(f"%{rule_name}%"))
        if item_id:
            conditions.append(AlarmRule.item_id == item_id)

        # 统计总数
        count_query = select(func.count(AlarmRule.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (select(AlarmRule)
                .where(and_(*conditions))
                .order_by(AlarmRule.created_at.desc())
                .offset(skip)
                .limit(size))
        result = await self.db.execute(query)
        alarmrules = list(result.scalars().all())

        return alarmrules, total

    async def update(self, alarmrule_id: str, data: Dict[str, Any]) -> Optional[AlarmRule]:
        """更新报警规则"""
        alarmrule = await self.get_by_id(alarmrule_id)
        if not alarmrule:
            raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

        for key, value in data.items():
            setattr(alarmrule, key, value)

        await self.db.commit()
        await self.db.refresh(alarmrule)
        return alarmrule

    async def delete(self, alarmrule_id: str) -> bool:
        """删除报警规则（软删除）"""
        alarmrule = await self.get_by_id(alarmrule_id)
        if not alarmrule:
            raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

        alarmrule.is_deleted = True
        await self.db.commit()
        return True

    async def exists_by_name(self, rule_name: str, exclude_id: str = None) -> bool:
        """检查规则名称是否已存在"""
        conditions = [
            AlarmRule.rule_name == rule_name,
            AlarmRule.is_deleted == False
        ]
        if exclude_id:
            conditions.append(AlarmRule.id != exclude_id)

        query = select(AlarmRule).where(and_(*conditions))
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count_all(self) -> int:
        """统计所有报警规则数量"""
        stmt = select(func.count(AlarmRule.id)).where(AlarmRule.is_deleted == False)
        result = await self.db.execute(stmt)
        return result.scalar() or 0

