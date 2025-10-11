"""
报警规则业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.alarmrule_repository import AlarmRuleRepository
from ..repositories.item_repository import ItemRepository
from ..schemas.alarmrule import AlarmRuleCreate, AlarmRuleUpdate, AlarmRuleQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class AlarmRuleService:
    """报警规则业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alarmrule_repo = AlarmRuleRepository(db)
        self.item_repo = ItemRepository(db)

    async def create_alarmrule(self, alarmrule_data: AlarmRuleCreate, user: dict) -> Dict[str, Any]:
        """创建报警规则"""
        try:
            # 检查规则名称是否已存在
            if await self.alarmrule_repo.exists_by_name(alarmrule_data.rule_name):
                raise BusinessError(f"规则名称 '{alarmrule_data.rule_name}' 已存在")

            # 验证巡检项目是否存在
            item = await self.item_repo.get_by_id(alarmrule_data.item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{alarmrule_data.item_id}' 不存在")

            create_data = alarmrule_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            alarmrule = await self.alarmrule_repo.create(create_data)

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

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建报警规则失败: {e}")
            raise HTTPException(status_code=500, detail="创建报警规则失败")

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
            logger.error(f"获取报警规则失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警规则失败")

    async def get_alarmrules_by_ids(self, alarmrule_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取报警规则"""
        try:
            alarmrules = await self.alarmrule_repo.get_by_ids(alarmrule_ids)

            items_data = [self._format_alarmrule_response(alarmrule) for alarmrule in alarmrules]

            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取报警规则列表成功"
            )

        except Exception as e:
            logger.error(f"获取报警规则列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警规则列表失败")

    async def get_alarmrules(self, query: AlarmRuleQuery, user: dict) -> Dict[str, Any]:
        """获取报警规则列表（分页）"""
        try:
            alarmrules, total = await self.alarmrule_repo.get_all(
                page=query.page,
                size=query.size,
                rule_name=query.rule_name,
                item_id=query.item_id
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
            logger.error(f"获取报警规则列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警规则列表失败")

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

            # 如果更新巡检项目ID，验证新项目是否存在
            if alarmrule_data.item_id:
                item = await self.item_repo.get_by_id(alarmrule_data.item_id)
                if not item:
                    raise ResourceNotFoundError(f"巡检项目ID '{alarmrule_data.item_id}' 不存在")

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
            logger.error(f"更新报警规则失败: {e}")
            raise HTTPException(status_code=500, detail="更新报警规则失败")

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

                return ApiResponse.success(message="删除报警规则成功")
            else:
                raise HTTPException(status_code=500, detail="删除报警规则失败")

        except ResourceNotFoundError as e:
            logger.warning(f"删除报警规则失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除报警规则失败: {e}")
            raise HTTPException(status_code=500, detail="删除报警规则失败")

    async def get_alarmrule_stats(self, user: dict) -> Dict[str, Any]:
        """获取报警规则统计信息"""
        try:
            total_count = await self.alarmrule_repo.count_all()

            stats = {
                "total_alarmrules": total_count
            }

            return ApiResponse.success(
                data=stats,
                message="获取报警规则统计成功"
            )

        except Exception as e:
            logger.error(f"获取报警规则统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警规则统计失败")

    def _format_alarmrule_response(self, alarmrule) -> Dict[str, Any]:
        """格式化报警规则响应数据"""
        return {
            "id": alarmrule.id,
            "rule_name": alarmrule.rule_name,
            "item_id": alarmrule.item_id,
            "alarm_param": alarmrule.alarm_param,
            "created_at": alarmrule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if alarmrule.created_at else None,
            "updated_at": alarmrule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if alarmrule.updated_at else None,
            "created_by": alarmrule.created_by,
            "updated_by": alarmrule.updated_by,
        }

