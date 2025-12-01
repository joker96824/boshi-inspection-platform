"""
报警规则数据仓库
"""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

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
        """根据ID获取报警规则（预加载关联关系）"""
        query = (
            select(AlarmRule)
            .options(selectinload(AlarmRule.relations))
            .where(AlarmRule.id == alarmrule_id, AlarmRule.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_ids(self, alarmrule_ids: List[str]) -> List[AlarmRule]:
        """根据ID列表获取报警规则"""
        if not alarmrule_ids:
            return []

        query = (
            select(AlarmRule)
            .options(selectinload(AlarmRule.relations))
            .where(
                AlarmRule.id.in_(alarmrule_ids),
                AlarmRule.is_deleted == False
            )
            .order_by(AlarmRule.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_all(self, page: Optional[int] = None, size: Optional[int] = None,
                     rule_name: str = None, alarm_category: str = None,
                     alarm_level: int = None, rule_type: str = None,
                     enabled: bool = None, is_global: bool = None) -> Tuple[List[AlarmRule], int]:
        """获取报警规则列表（分页）"""
        if page is None or size is None:
            skip = None
            limit = None
        else:
            skip = (page - 1) * size
            limit = size

        # 构建查询条件
        conditions = [AlarmRule.is_deleted == False]

        if rule_name:
            conditions.append(AlarmRule.rule_name.like(f"%{rule_name}%"))
        if alarm_category:
            conditions.append(AlarmRule.alarm_category == alarm_category)
        if alarm_level is not None:
            conditions.append(AlarmRule.alarm_level == alarm_level)
        if rule_type:
            conditions.append(AlarmRule.rule_type == rule_type)
        if enabled is not None:
            conditions.append(AlarmRule.enabled == enabled)
        if is_global is not None:
            conditions.append(AlarmRule.is_global == is_global)

        # 统计总数
        count_query = select(func.count(AlarmRule.id)).where(and_(*conditions))
        count_result = await self.db.execute(count_query)
        total = count_result.scalar() or 0

        # 查询数据
        query = (
            select(AlarmRule)
            .options(selectinload(AlarmRule.relations))
            .where(and_(*conditions))
            .order_by(AlarmRule.created_at.desc(), AlarmRule.id.desc())
        )
        if skip is not None and limit is not None:
            query = query.offset(skip).limit(limit)

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

    async def get_by_relation(self, relation_type: str, relation_id: str) -> List[AlarmRule]:
        """根据关联对象获取报警规则列表"""
        from ..models.alarmrulerelation import AlarmRuleRelation

        query = (
            select(AlarmRule)
            .join(AlarmRuleRelation, AlarmRule.id == AlarmRuleRelation.alarm_rule_id)
            .options(selectinload(AlarmRule.relations))
            .where(
                AlarmRuleRelation.relation_type == relation_type,
                AlarmRuleRelation.relation_id == relation_id,
                AlarmRule.is_deleted == False,
                AlarmRule.enabled == True
            )
            .order_by(AlarmRule.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_global_rules(self, alarm_category: str) -> List[AlarmRule]:
        """获取全局规则列表"""
        query = (
            select(AlarmRule)
            .options(selectinload(AlarmRule.relations))
            .where(
                AlarmRule.is_global == True,
                AlarmRule.alarm_category == alarm_category,
                AlarmRule.enabled == True,
                AlarmRule.is_deleted == False
            )
            .order_by(AlarmRule.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
