"""
电机状态配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.motorstatus_repository import MotorStatusRepository
from ..schemas.motorstatus import MotorStatusCreate, MotorStatusUpdate, MotorStatusQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class MotorStatusService:
    """电机状态配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = MotorStatusRepository(db)

    async def create_motor_status(self, data: MotorStatusCreate, user: dict) -> Dict[str, Any]:
        """创建电机状态配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建电机状态配置
            motor_status = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_motor_status",
                f"创建电机状态配置: 电机ID{motor_status.motor_id}, 波特率{motor_status.baud_rate}",
                extra={"status_id": motor_status.id, "motor_id": motor_status.motor_id, "baud_rate": motor_status.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_status_response(motor_status),
                message="电机状态配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建电机状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建电机状态配置失败: {str(e)}")

    async def get_motor_status_by_id(self, status_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取电机状态配置"""
        try:
            motor_status = await self.repo.get_by_id(status_id)
            if not motor_status:
                raise ResourceNotFoundError(f"电机状态配置ID '{status_id}' 不存在")

            return ApiResponse.success(
                data=self._format_status_response(motor_status),
                message="获取电机状态配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取电机状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取电机状态配置失败: {str(e)}")

    async def get_motor_statuses_by_ids(self, motorstatus_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取电机状态配置"""
        try:
            motor_statuses = await self.repo.get_by_ids(motorstatus_ids)
            if not motor_statuses:
                raise ResourceNotFoundError("未找到任何电机状态配置")

            return ApiResponse.success(
                data=[self._format_status_response(status) for status in motor_statuses],
                message=f"成功获取 {len(motor_statuses)} 个电机状态配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取电机状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取电机状态配置失败: {str(e)}")

    async def get_motor_statuses(self, query: MotorStatusQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取电机状态配置列表"""
        try:
            motor_statuses, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                motor_id=query.motor_id,
                baud_rate=query.baud_rate
            )

            return ApiResponse.paginated(
                items=[self._format_status_response(status) for status in motor_statuses],
                total=total,
                page=query.page,
                size=query.size,
                message="获取电机状态配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取电机状态配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取电机状态配置列表失败: {str(e)}")

    async def update_motor_status(self, status_id: str, data: MotorStatusUpdate, user: dict) -> Dict[str, Any]:
        """更新电机状态配置"""
        try:
            # 检查电机状态配置是否存在
            existing_status = await self.repo.get_by_id(status_id)
            if not existing_status:
                raise ResourceNotFoundError(f"电机状态配置ID '{status_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新电机状态配置
            motor_status = await self.repo.update(status_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_motor_status",
                f"更新电机状态配置: 电机ID{motor_status.motor_id}, 波特率{motor_status.baud_rate}",
                extra={"status_id": motor_status.id, "motor_id": motor_status.motor_id, "baud_rate": motor_status.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_status_response(motor_status),
                message="电机状态配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新电机状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新电机状态配置失败: {str(e)}")

    async def delete_motor_status(self, status_id: str, user: dict) -> Dict[str, Any]:
        """删除电机状态配置"""
        try:
            # 检查电机状态配置是否存在
            existing_status = await self.repo.get_by_id(status_id)
            if not existing_status:
                raise ResourceNotFoundError(f"电机状态配置ID '{status_id}' 不存在")

            # 软删除电机状态配置
            success = await self.repo.soft_delete(status_id, user["username"])
            if not success:
                raise BusinessError(f"删除电机状态配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_motor_status",
                f"删除电机状态配置: 电机ID{existing_status.motor_id}, 波特率{existing_status.baud_rate}",
                extra={"status_id": status_id, "motor_id": existing_status.motor_id, "baud_rate": existing_status.baud_rate}
            )

            return ApiResponse.success(
                data={"id": status_id},
                message="电机状态配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除电机状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除电机状态配置失败: {str(e)}")

    async def get_motor_status_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取电机状态配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取电机状态配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取电机状态配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取电机状态配置统计信息失败: {str(e)}")

    def _format_status_response(self, motor_status) -> Dict[str, Any]:
        """格式化电机状态配置响应数据"""
        return {
            "id": motor_status.id,
            "motor_id": motor_status.motor_id,
            "baud_rate": motor_status.baud_rate,
            "tpdo_config": motor_status.tpdo_config,
            "rpdo_config": motor_status.rpdo_config,
            "created_at": motor_status.created_at.strftime("%Y-%m-%dT%H:%M:%S") if motor_status.created_at else None,
            "updated_at": motor_status.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if motor_status.updated_at else None,
            "created_by": motor_status.created_by,
            "updated_by": motor_status.updated_by,
        }
