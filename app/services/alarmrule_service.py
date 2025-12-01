"""
报警规则业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.alarmrule_repository import AlarmRuleRepository
from ..repositories.alarmrulerelation_repository import AlarmRuleRelationRepository
from ..repositories.item_repository import ItemRepository
from ..repositories.gimbal_repository import GimbalRepository
from ..repositories.sensor_repository import SensorRepository
from ..schemas.alarmrule import AlarmRuleCreate, AlarmRuleUpdate, AlarmRuleQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError, ValidationError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class AlarmRuleService:
    """报警规则业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alarmrule_repo = AlarmRuleRepository(db)
        self.relation_repo = AlarmRuleRelationRepository(db)
        self.item_repo = ItemRepository(db)
        self.gimbal_repo = GimbalRepository(db)
        self.sensor_repo = SensorRepository(db)

    async def create_alarmrule(self, alarmrule_data: AlarmRuleCreate, user: dict) -> Dict[str, Any]:
        """创建报警规则"""
        try:
            # 检查规则名称是否已存在
            if await self.alarmrule_repo.exists_by_name(alarmrule_data.rule_name):
                raise BusinessError(f"规则名称 '{alarmrule_data.rule_name}' 已存在")

            # 验证关联对象
            if not alarmrule_data.is_global:
                await self._validate_relations(alarmrule_data.alarm_category, alarmrule_data.relations)

            # 创建报警规则
            create_data = alarmrule_data.dict(exclude={'relations'})
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            alarmrule = await self.alarmrule_repo.create(create_data)

            # 创建关联关系
            if not alarmrule_data.is_global and alarmrule_data.relations:
                for relation in alarmrule_data.relations:
                    relation_data = {
                        "alarm_rule_id": alarmrule.id,
                        "relation_type": relation.type,
                        "relation_id": relation.id,
                        "sort_order": relation.sort_order,
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    }
                    await self.relation_repo.create(relation_data)

            # 重新查询以加载关联关系
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule.id)

            log_user_action(
                user["username"],
                "create_alarmrule",
                "success",
                f"创建报警规则成功，ID: {alarmrule.id}"
            )

            return ApiResponse.success(
                data=self._format_alarmrule_response(alarmrule),
                message="创建报警规则成功"
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"创建报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建报警规则失败: {e}", exc_info=True)
            raise BusinessError(f"创建报警规则失败: {str(e)}")

    async def get_alarmrule_by_id(self, alarmrule_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取报警规则"""
        try:
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            return ApiResponse.success(
                data=self._format_alarmrule_response(alarmrule),
                message="获取报警规则成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取报警规则失败: {e}", exc_info=True)
            raise BusinessError(f"获取报警规则失败: {str(e)}")

    async def get_alarmrules(self, query: AlarmRuleQuery, user: dict) -> Dict[str, Any]:
        """获取报警规则列表（分页）"""
        try:
            alarmrules, total = await self.alarmrule_repo.get_all(
                page=query.page,
                size=query.size,
                rule_name=query.rule_name,
                alarm_category=query.alarm_category,
                alarm_level=query.alarm_level,
                rule_type=query.rule_type,
                enabled=query.enabled,
                is_global=query.is_global
            )

            items_data = [self._format_alarmrule_response(alarmrule) for alarmrule in alarmrules]

            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取报警规则列表成功"
            )

        except Exception as e:
            logger.error(f"获取报警规则列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取报警规则列表失败: {str(e)}")

    async def update_alarmrule(self, alarmrule_id: str, alarmrule_data: AlarmRuleUpdate, user: dict) -> Dict[str, Any]:
        """更新报警规则"""
        try:
            existing_alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not existing_alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            # 如果更新规则名称，检查新名称是否已存在
            if alarmrule_data.rule_name and alarmrule_data.rule_name != existing_alarmrule.rule_name:
                if await self.alarmrule_repo.exists_by_name(alarmrule_data.rule_name, alarmrule_id):
                    raise BusinessError(f"规则名称 '{alarmrule_data.rule_name}' 已存在")

            update_data = alarmrule_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]

            updated_alarmrule = await self.alarmrule_repo.update(alarmrule_id, update_data)

            log_user_action(
                user["username"],
                "update_alarmrule",
                "success",
                f"更新报警规则成功，ID: {alarmrule_id}"
            )

            return ApiResponse.success(
                data=self._format_alarmrule_response(updated_alarmrule),
                message="更新报警规则成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新报警规则失败: {e}", exc_info=True)
            raise BusinessError(f"更新报警规则失败: {str(e)}")

    async def delete_alarmrule(self, alarmrule_id: str, user: dict) -> Dict[str, Any]:
        """删除报警规则（软删除）"""
        try:
            existing_alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not existing_alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            success = await self.alarmrule_repo.delete(alarmrule_id)

            if success:
                log_user_action(
                    user["username"],
                    "delete_alarmrule",
                    "success",
                    f"删除报警规则成功，ID: {alarmrule_id}"
                )

                return ApiResponse.success(
                    data={"id": alarmrule_id},
                    message="删除报警规则成功"
                )
            else:
                raise BusinessError("删除报警规则失败")

        except ResourceNotFoundError as e:
            logger.warning(f"删除报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除报警规则失败: {e}", exc_info=True)
            raise BusinessError(f"删除报警规则失败: {str(e)}")

    async def enable_alarmrule(self, alarmrule_id: str, enabled: bool, user: dict) -> Dict[str, Any]:
        """启用/禁用报警规则"""
        try:
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            update_data = {
                "enabled": enabled,
                "updated_by": user["username"]
            }
            updated_alarmrule = await self.alarmrule_repo.update(alarmrule_id, update_data)

            log_user_action(
                user["username"],
                "enable_alarmrule" if enabled else "disable_alarmrule",
                "success",
                f"{'启用' if enabled else '禁用'}报警规则成功，ID: {alarmrule_id}"
            )

            return ApiResponse.success(
                data=self._format_alarmrule_response(updated_alarmrule),
                message=f"{'启用' if enabled else '禁用'}报警规则成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"{'启用' if enabled else '禁用'}报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"{'启用' if enabled else '禁用'}报警规则失败: {e}", exc_info=True)
            raise BusinessError(f"{'启用' if enabled else '禁用'}报警规则失败: {str(e)}")

    async def add_relations(self, alarmrule_id: str, relations: List[Dict[str, Any]], user: dict) -> Dict[str, Any]:
        """为报警规则添加关联对象"""
        try:
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            if alarmrule.is_global:
                raise BusinessError("全局规则不能关联对象")

            # 验证关联对象
            relation_items = [type('obj', (object,), r)() for r in relations]
            await self._validate_relations(alarmrule.alarm_category, relation_items)

            # 添加关联
            for relation in relations:
                if not await self.relation_repo.exists(alarmrule_id, relation["type"], relation["id"]):
                    relation_data = {
                        "alarm_rule_id": alarmrule_id,
                        "relation_type": relation["type"],
                        "relation_id": relation["id"],
                        "sort_order": relation.get("sort_order", 0),
                        "created_by": user["username"],
                        "updated_by": user["username"]
                    }
                    await self.relation_repo.create(relation_data)

            # 重新查询
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)

            return ApiResponse.success(
                data=self._format_alarmrule_response(alarmrule),
                message="添加关联对象成功"
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"添加关联对象失败: {e}")
            raise
        except Exception as e:
            logger.error(f"添加关联对象失败: {e}", exc_info=True)
            raise BusinessError(f"添加关联对象失败: {str(e)}")

    async def remove_relations(self, alarmrule_id: str, relations: List[Dict[str, Any]], user: dict) -> Dict[str, Any]:
        """删除报警规则的关联对象"""
        try:
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            # 删除关联
            for relation in relations:
                await self.relation_repo.delete_by_rule_and_relation(
                    alarmrule_id, relation["type"], relation["id"]
                )

            # 重新查询
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)

            return ApiResponse.success(
                data=self._format_alarmrule_response(alarmrule),
                message="删除关联对象成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"删除关联对象失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除关联对象失败: {e}", exc_info=True)
            raise BusinessError(f"删除关联对象失败: {str(e)}")

    async def get_relations(self, alarmrule_id: str, user: dict) -> Dict[str, Any]:
        """获取报警规则的关联对象列表"""
        try:
            alarmrule = await self.alarmrule_repo.get_by_id(alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarmrule_id}' 不存在")

            relations = await self.relation_repo.get_by_rule_id_ordered(alarmrule_id)
            relations_data = [
                {
                    "id": r.id,
                    "type": r.relation_type,
                    "relation_id": r.relation_id,
                    "sort_order": r.sort_order,
                    "created_at": r.created_at.strftime("%Y-%m-%dT%H:%M:%S") if r.created_at else None,
                }
                for r in relations
            ]

            return ApiResponse.success(
                data={"relations": relations_data},
                message="获取关联对象列表成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取关联对象列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取关联对象列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取关联对象列表失败: {str(e)}")

    async def _validate_relations(self, alarm_category: str, relations: List) -> None:
        """验证关联关系是否合法"""
        if not relations:
            raise ValidationError("非全局规则必须至少关联一个对象")

        # 验证关联类型与报警分类的匹配性
        valid_types = {
            'robot': [],
            'inspection': ['item'],
            'gimbal': ['gimbal'],
            'sensor': ['sensor'],
            'other': ['item', 'gimbal', 'sensor']
        }

        allowed_types = valid_types.get(alarm_category, [])
        if not allowed_types:
            # robot类型通常不关联对象
            return

        for relation in relations:
            if relation.type not in allowed_types:
                raise ValidationError(
                    f"报警分类 '{alarm_category}' 只能关联类型: {', '.join(allowed_types)}"
                )

            # 验证关联对象是否存在
            if relation.type == 'item':
                item = await self.item_repo.get_by_id(relation.id)
                if not item:
                    raise ResourceNotFoundError(f"巡检项目ID '{relation.id}' 不存在")
            elif relation.type == 'gimbal':
                gimbal = await self.gimbal_repo.get_by_id(relation.id)
                if not gimbal:
                    raise ResourceNotFoundError(f"云台ID '{relation.id}' 不存在")
            elif relation.type == 'sensor':
                sensor = await self.sensor_repo.get_by_id(relation.id)
                if not sensor:
                    raise ResourceNotFoundError(f"传感器ID '{relation.id}' 不存在")

    def _format_alarmrule_response(self, alarmrule) -> Dict[str, Any]:
        """格式化报警规则响应数据"""
        relations_data = []
        if alarmrule.relations:
            for relation in alarmrule.relations:
                relations_data.append({
                    "id": relation.id,
                    "type": relation.relation_type,
                    "relation_id": relation.relation_id,
                    "sort_order": relation.sort_order,
                })

        return {
            "id": alarmrule.id,
            "rule_name": alarmrule.rule_name,
            "alarm_category": alarmrule.alarm_category,
            "alarm_level": alarmrule.alarm_level,
            "rule_type": alarmrule.rule_type,
            "rule_config": alarmrule.rule_config,
            "enabled": alarmrule.enabled,
            "description": alarmrule.description,
            "is_global": alarmrule.is_global,
            "relations": relations_data,
            "created_at": alarmrule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if alarmrule.created_at else None,
            "updated_at": alarmrule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if alarmrule.updated_at else None,
            "created_by": alarmrule.created_by,
            "updated_by": alarmrule.updated_by,
        }
