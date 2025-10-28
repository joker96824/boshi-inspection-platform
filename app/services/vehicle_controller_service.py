"""
车体控制器业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.vehiclecontroller_repository import VehicleControllerRepository
from ..schemas.vehiclecontroller import VehicleControllerCreate, VehicleControllerUpdate, VehicleControllerQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class VehicleControllerService:
    """车体控制器业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = VehicleControllerRepository(db)

    async def create_controller(self, data: VehicleControllerCreate, user: dict) -> Dict[str, Any]:
        """创建车体控制器"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建车体控制器
            controller = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_vehicle_controller",
                f"创建车体控制器: {controller.vehicle_model}",
                extra={"controller_id": controller.id, "vehicle_model": controller.vehicle_model}
            )

            return ApiResponse.success(
                data=self._format_controller_response(controller),
                message="车体控制器创建成功"
            )

        except BusinessError:
            raise
        except Exception as e:
            logger.error(f"创建车体控制器失败: {e}", exc_info=True)
            raise BusinessError(f"创建车体控制器失败: {str(e)}")

    async def get_controller_by_id(self, controller_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取车体控制器"""
        try:
            controller = await self.repo.get_by_id(controller_id)
            if not controller:
                raise ResourceNotFoundError(f"车体控制器ID '{controller_id}' 不存在")

            return ApiResponse.success(
                data=self._format_controller_response(controller),
                message="获取车体控制器成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取车体控制器失败: {e}", exc_info=True)
            raise BusinessError(f"获取车体控制器失败: {str(e)}")

    async def get_controllers_by_ids(self, vehiclecontroller_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取车体控制器"""
        try:
            controllers = await self.repo.get_by_ids(vehiclecontroller_ids)
            if not controllers:
                raise ResourceNotFoundError("未找到任何车体控制器")

            return ApiResponse.success(
                data=[self._format_controller_response(controller) for controller in controllers],
                message=f"成功获取 {len(controllers)} 个车体控制器"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取车体控制器失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取车体控制器失败: {str(e)}")

    async def get_controllers(self, query: VehicleControllerQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取车体控制器列表"""
        try:
            controllers, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                vehicle_model=query.vehicle_model
            )

            return ApiResponse.paginated(
                items=[self._format_controller_response(controller) for controller in controllers],
                total=total,
                page=query.page,
                size=query.size,
                message="获取车体控制器列表成功"
            )

        except Exception as e:
            logger.error(f"获取车体控制器列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取车体控制器列表失败: {str(e)}")

    async def update_controller(self, controller_id: str, data: VehicleControllerUpdate, user: dict) -> Dict[str, Any]:
        """更新车体控制器"""
        try:
            # 检查车体控制器是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"车体控制器ID '{controller_id}' 不存在")


            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新车体控制器
            controller = await self.repo.update(controller_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_vehicle_controller",
                f"更新车体控制器: {controller.vehicle_model}",
                extra={"controller_id": controller.id, "vehicle_model": controller.vehicle_model}
            )

            return ApiResponse.success(
                data=self._format_controller_response(controller),
                message="车体控制器更新成功"
            )

        except (ResourceNotFoundError, BusinessError):
            raise
        except Exception as e:
            logger.error(f"更新车体控制器失败: {e}", exc_info=True)
            raise BusinessError(f"更新车体控制器失败: {str(e)}")

    async def delete_controller(self, controller_id: str, user: dict) -> Dict[str, Any]:
        """删除车体控制器"""
        try:
            # 检查车体控制器是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"车体控制器ID '{controller_id}' 不存在")

            # 软删除车体控制器
            success = await self.repo.soft_delete(controller_id, user["username"])
            if not success:
                raise BusinessError("删除车体控制器失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_vehicle_controller",
                f"删除车体控制器: {existing_controller.vehicle_model}",
                extra={"controller_id": controller_id, "vehicle_model": existing_controller.vehicle_model}
            )

            return ApiResponse.success(
                data={"id": controller_id},
                message="车体控制器删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除车体控制器失败: {e}", exc_info=True)
            raise BusinessError(f"删除车体控制器失败: {str(e)}")

    async def get_controller_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取车体控制器统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取车体控制器统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取车体控制器统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取车体控制器统计信息失败: {str(e)}")

    def _format_controller_response(self, controller) -> Dict[str, Any]:
        """格式化车体控制器响应数据"""
        return {
            "id": controller.id,
            "vehicle_model": controller.vehicle_model,
            "wheel_diameter": float(controller.wheel_diameter),
            "reduction_ratio": controller.reduction_ratio,
            "wheelbase": float(controller.wheelbase),
            "track_width": float(controller.track_width),
            "max_linear_velocity": float(controller.max_linear_velocity),
            "max_angular_velocity": float(controller.max_angular_velocity),
            "serial_configs": controller.serial_configs,
            "ethernet_configs": controller.ethernet_configs,
            "controller_version": controller.controller_version,
            "remote_upgrade_enabled": controller.remote_upgrade_enabled,
            "created_at": controller.created_at.strftime("%Y-%m-%dT%H:%M:%S") if controller.created_at else None,
            "updated_at": controller.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if controller.updated_at else None,
            "created_by": controller.created_by,
            "updated_by": controller.updated_by,
        }
