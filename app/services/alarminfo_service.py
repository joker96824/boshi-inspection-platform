"""
报警信息业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.alarminfo_repository import AlarmInfoRepository
from ..repositories.alarmrule_repository import AlarmRuleRepository
from ..repositories.itemhistory_repository import ItemHistoryRepository
from ..schemas.alarminfo import AlarmInfoCreate, AlarmInfoUpdate, AlarmInfoQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class AlarmInfoService:
    """报警信息业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.alarminfo_repo = AlarmInfoRepository(db)
        self.alarmrule_repo = AlarmRuleRepository(db)
        self.itemhistory_repo = ItemHistoryRepository(db)

    async def create_alarminfo(self, alarminfo_data: AlarmInfoCreate, user: dict) -> Dict[str, Any]:
        """创建报警信息"""
        try:
            # 验证报警规则是否存在
            alarmrule = await self.alarmrule_repo.get_by_id(alarminfo_data.alarmrule_id)
            if not alarmrule:
                raise ResourceNotFoundError(f"报警规则ID '{alarminfo_data.alarmrule_id}' 不存在")

            # 验证巡检记录是否存在
            itemhistory = await self.itemhistory_repo.get_by_id(alarminfo_data.itemhistory_id)
            if not itemhistory:
                raise ResourceNotFoundError(f"巡检记录ID '{alarminfo_data.itemhistory_id}' 不存在")

            create_data = alarminfo_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            alarminfo = await self.alarminfo_repo.create(create_data)

            log_user_action(
                user["username"],
                "create_alarminfo",
                "success",
                f"创建报警信息成功，ID: {alarminfo.id}"
            )

            return ApiResponse.success(
                data=self._format_alarminfo_response(alarminfo),
                message="创建报警信息成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建报警信息失败: {e}")
            raise HTTPException(status_code=500, detail="创建报警信息失败")

    async def get_alarminfo_by_id(self, alarminfo_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取报警信息"""
        try:
            alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            return ApiResponse.success(
                data=self._format_alarminfo_response(alarminfo),
                message="获取报警信息成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取报警信息失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警信息失败")

    async def get_alarminfos_by_ids(self, alarminfo_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取报警信息"""
        try:
            alarminfos = await self.alarminfo_repo.get_by_ids(alarminfo_ids)

            items_data = [self._format_alarminfo_response(alarminfo) for alarminfo in alarminfos]

            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取报警信息列表成功"
            )

        except Exception as e:
            logger.error(f"获取报警信息列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警信息列表失败")

    async def get_alarminfos(self, query: AlarmInfoQuery, user: dict) -> Dict[str, Any]:
        """获取报警信息列表（分页）"""
        try:
            alarminfos, total = await self.alarminfo_repo.get_all(
                page=query.page,
                size=query.size,
                alarmrule_id=query.alarmrule_id,
                itemhistory_id=query.itemhistory_id
            )

            items_data = [self._format_alarminfo_response(alarminfo) for alarminfo in alarminfos]

            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取报警信息列表成功"
            )

        except Exception as e:
            logger.error(f"获取报警信息列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警信息列表失败")

    async def update_alarminfo(self, alarminfo_id: str, alarminfo_data: AlarmInfoUpdate, user: dict) -> Dict[str, Any]:
        """更新报警信息"""
        try:
            existing_alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not existing_alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            # 如果更新报警规则ID，验证新规则是否存在
            if alarminfo_data.alarmrule_id:
                alarmrule = await self.alarmrule_repo.get_by_id(alarminfo_data.alarmrule_id)
                if not alarmrule:
                    raise ResourceNotFoundError(f"报警规则ID '{alarminfo_data.alarmrule_id}' 不存在")

            # 如果更新巡检记录ID，验证新记录是否存在
            if alarminfo_data.itemhistory_id:
                itemhistory = await self.itemhistory_repo.get_by_id(alarminfo_data.itemhistory_id)
                if not itemhistory:
                    raise ResourceNotFoundError(f"巡检记录ID '{alarminfo_data.itemhistory_id}' 不存在")

            update_data = alarminfo_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]

            updated_alarminfo = await self.alarminfo_repo.update(alarminfo_id, update_data)

            log_user_action(
                user["username"],
                "update_alarminfo",
                "success",
                f"更新报警信息成功，ID: {alarminfo_id}"
            )

            return ApiResponse.success(
                data=self._format_alarminfo_response(updated_alarminfo),
                message="更新报警信息成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新报警信息失败: {e}")
            raise HTTPException(status_code=500, detail="更新报警信息失败")

    async def delete_alarminfo(self, alarminfo_id: str, user: dict) -> Dict[str, Any]:
        """删除报警信息（软删除）"""
        try:
            existing_alarminfo = await self.alarminfo_repo.get_by_id(alarminfo_id)
            if not existing_alarminfo:
                raise ResourceNotFoundError(f"报警信息ID '{alarminfo_id}' 不存在")

            success = await self.alarminfo_repo.delete(alarminfo_id)

            if success:
                log_user_action(
                    user["username"],
                    "delete_alarminfo",
                    "success",
                    f"删除报警信息成功，ID: {alarminfo_id}"
                )

                return ApiResponse.success(message="删除报警信息成功")
            else:
                raise HTTPException(status_code=500, detail="删除报警信息失败")

        except ResourceNotFoundError as e:
            logger.warning(f"删除报警信息失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除报警信息失败: {e}")
            raise HTTPException(status_code=500, detail="删除报警信息失败")

    async def get_alarminfo_stats(self, user: dict) -> Dict[str, Any]:
        """获取报警信息统计信息"""
        try:
            total_count = await self.alarminfo_repo.count_all()

            stats = {
                "total_alarminfos": total_count
            }

            return ApiResponse.success(
                data=stats,
                message="获取报警信息统计成功"
            )

        except Exception as e:
            logger.error(f"获取报警信息统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取报警信息统计失败")

    def _format_alarminfo_response(self, alarminfo) -> Dict[str, Any]:
        """格式化报警信息响应数据"""
        return {
            "id": alarminfo.id,
            "alarmrule_id": alarminfo.alarmrule_id,
            "itemhistory_id": alarminfo.itemhistory_id,
            "alarm_data": alarminfo.alarm_data,
            "alarm_info": alarminfo.alarm_info,
            "created_at": alarminfo.created_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.created_at else None,
            "updated_at": alarminfo.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if alarminfo.updated_at else None,
            "created_by": alarminfo.created_by,
            "updated_by": alarminfo.updated_by,
        }

