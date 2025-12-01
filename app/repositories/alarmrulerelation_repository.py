"""
报警规则关联数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_

from ..models.alarmrulerelation import AlarmRuleRelation
from ..core.exceptions import ResourceNotFoundError


class AlarmRuleRelationRepository:
    """报警规则关联数据仓库（使用物理删除）"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, data: Dict[str, Any]) -> AlarmRuleRelation:
        """创建关联"""
        relation = AlarmRuleRelation(**data)
        self.db.add(relation)
        await self.db.commit()
        await self.db.refresh(relation)
        return relation

    async def get_by_id(self, relation_id: str) -> Optional[AlarmRuleRelation]:
        """根据ID获取关联"""
        query = select(AlarmRuleRelation).where(AlarmRuleRelation.id == relation_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_rule_id_ordered(self, alarm_rule_id: str) -> List[AlarmRuleRelation]:
        """根据规则ID获取所有关联（按sort_order排序）"""
        query = (
            select(AlarmRuleRelation)
            .where(AlarmRuleRelation.alarm_rule_id == alarm_rule_id)
            .order_by(AlarmRuleRelation.sort_order.asc(), AlarmRuleRelation.id.asc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_rule_id(self, alarm_rule_id: str) -> List[AlarmRuleRelation]:
        """根据规则ID获取所有关联"""
        query = select(AlarmRuleRelation).where(AlarmRuleRelation.alarm_rule_id == alarm_rule_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_relation(self, relation_type: str, relation_id: str) -> List[AlarmRuleRelation]:
        """根据关联对象获取关联列表"""
        query = select(AlarmRuleRelation).where(
            AlarmRuleRelation.relation_type == relation_type,
            AlarmRuleRelation.relation_id == relation_id
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def delete_by_id(self, relation_id: str) -> bool:
        """删除关联（物理删除）"""
        relation = await self.get_by_id(relation_id)
        if not relation:
            raise ResourceNotFoundError(f"关联ID '{relation_id}' 不存在")

        stmt = delete(AlarmRuleRelation).where(AlarmRuleRelation.id == relation_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def delete_by_rule_and_relation(self, alarm_rule_id: str, relation_type: str, relation_id: str) -> bool:
        """删除特定关联（物理删除）"""
        stmt = delete(AlarmRuleRelation).where(
            AlarmRuleRelation.alarm_rule_id == alarm_rule_id,
            AlarmRuleRelation.relation_type == relation_type,
            AlarmRuleRelation.relation_id == relation_id
        )
        result = await self.db.execute(stmt)
        await self.db.commit()
        return result.rowcount > 0

    async def delete_by_rule_id(self, alarm_rule_id: str) -> bool:
        """删除规则的所有关联（物理删除）"""
        stmt = delete(AlarmRuleRelation).where(AlarmRuleRelation.alarm_rule_id == alarm_rule_id)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def exists(self, alarm_rule_id: str, relation_type: str, relation_id: str) -> bool:
        """检查关联是否存在"""
        query = select(AlarmRuleRelation).where(
            AlarmRuleRelation.alarm_rule_id == alarm_rule_id,
            AlarmRuleRelation.relation_type == relation_type,
            AlarmRuleRelation.relation_id == relation_id
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

