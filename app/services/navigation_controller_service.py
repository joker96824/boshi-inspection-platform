"""
导航控制器配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.navigationcontroller_repository import NavigationControllerRepository
from ..schemas.navigationcontroller import NavigationControllerCreate, NavigationControllerUpdate, NavigationControllerQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class NavigationControllerService:
    """导航控制器配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NavigationControllerRepository(db)

    async def create_navigation_controller(self, data: NavigationControllerCreate, user: dict) -> Dict[str, Any]:
        """创建导航控制器配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建导航控制器配置
            navigation_controller = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_navigation_controller",
                f"创建导航控制器配置: 模块组{navigation_controller.module_group}",
                extra={"controller_id": navigation_controller.id, "module_group": navigation_controller.module_group}
            )

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="导航控制器配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建导航控制器配置失败: {str(e)}")

    async def get_navigation_controller_by_id(self, controller_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取导航控制器配置"""
        try:
            navigation_controller = await self.repo.get_by_id(controller_id)
            if not navigation_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="获取导航控制器配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers_by_ids(self, navigationcontroller_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取导航控制器配置"""
        try:
            navigation_controllers = await self.repo.get_by_ids(navigationcontroller_ids)
            if not navigation_controllers:
                raise ResourceNotFoundError("未找到任何导航控制器配置")

            return ApiResponse.success(
                data=[self._format_controller_response(controller) for controller in navigation_controllers],
                message=f"成功获取 {len(navigation_controllers)} 个导航控制器配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers_by_module_group(self, module_group: int, user: Optional[dict]) -> Dict[str, Any]:
        """根据模块组获取导航控制器配置"""
        try:
            navigation_controllers = await self.repo.get_by_module_group(module_group)
            if not navigation_controllers:
                raise ResourceNotFoundError(f"模块组 {module_group} 没有找到任何导航控制器配置")

            return ApiResponse.success(
                data=[self._format_controller_response(controller) for controller in navigation_controllers],
                message=f"成功获取模块组 {module_group} 的 {len(navigation_controllers)} 个导航控制器配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"根据模块组获取导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"根据模块组获取导航控制器配置失败: {str(e)}")

    async def get_navigation_controllers(self, query: NavigationControllerQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取导航控制器配置列表"""
        try:
            navigation_controllers, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                module_group=query.module_group,
                ethernet_ip=query.ethernet_ip,
                ethernet_port=query.ethernet_port,
                baud_rate=query.baud_rate
            )

            return ApiResponse.paginated(
                items=[self._format_controller_response(controller) for controller in navigation_controllers],
                total=total,
                page=query.page,
                size=query.size,
                message="获取导航控制器配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取导航控制器配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置列表失败: {str(e)}")

    async def update_navigation_controller(self, controller_id: str, data: NavigationControllerUpdate, user: dict) -> Dict[str, Any]:
        """更新导航控制器配置"""
        try:
            # 检查导航控制器配置是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新导航控制器配置
            navigation_controller = await self.repo.update(controller_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_navigation_controller",
                f"更新导航控制器配置: 模块组{navigation_controller.module_group}",
                extra={"controller_id": navigation_controller.id, "module_group": navigation_controller.module_group}
            )

            return ApiResponse.success(
                data=self._format_controller_response(navigation_controller),
                message="导航控制器配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新导航控制器配置失败: {str(e)}")

    async def delete_navigation_controller(self, controller_id: str, user: dict) -> Dict[str, Any]:
        """删除导航控制器配置"""
        try:
            # 检查导航控制器配置是否存在
            existing_controller = await self.repo.get_by_id(controller_id)
            if not existing_controller:
                raise ResourceNotFoundError(f"导航控制器配置ID '{controller_id}' 不存在")

            # 软删除导航控制器配置
            success = await self.repo.soft_delete(controller_id, user["username"])
            if not success:
                raise BusinessError(f"删除导航控制器配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_navigation_controller",
                f"删除导航控制器配置: 模块组{existing_controller.module_group}",
                extra={"controller_id": controller_id, "module_group": existing_controller.module_group}
            )

            return ApiResponse.success(
                data={"id": controller_id},
                message="导航控制器配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除导航控制器配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除导航控制器配置失败: {str(e)}")

    async def get_navigation_controller_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取导航控制器配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取导航控制器配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取导航控制器配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取导航控制器配置统计信息失败: {str(e)}")

    def _format_controller_response(self, navigation_controller) -> Dict[str, Any]:
        """格式化导航控制器配置响应数据"""
        return {
            "id": navigation_controller.id,
            "module_group": navigation_controller.module_group,
            "ethernet_ip": navigation_controller.ethernet_ip,
            "subnet_mask": navigation_controller.subnet_mask,
            "gateway": navigation_controller.gateway,
            "ethernet_port": navigation_controller.ethernet_port,
            "baud_rate": navigation_controller.baud_rate,
            "deceleration_distance": float(navigation_controller.deceleration_distance) if navigation_controller.deceleration_distance else 0.0,
            "stop_distance": float(navigation_controller.stop_distance) if navigation_controller.stop_distance else 0.0,
            "max_linear_velocity": float(navigation_controller.max_linear_velocity) if navigation_controller.max_linear_velocity else 0.0,
            "max_angular_velocity": float(navigation_controller.max_angular_velocity) if navigation_controller.max_angular_velocity else 0.0,
            "acceleration": float(navigation_controller.acceleration) if navigation_controller.acceleration else 0.0,
            "deceleration": float(navigation_controller.deceleration) if navigation_controller.deceleration else 0.0,
            "expansion_coefficient": float(navigation_controller.expansion_coefficient) if navigation_controller.expansion_coefficient else 0.0,
            "created_at": navigation_controller.created_at.strftime("%Y-%m-%dT%H:%M:%S") if navigation_controller.created_at else None,
            "updated_at": navigation_controller.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if navigation_controller.updated_at else None,
            "created_by": navigation_controller.created_by,
            "updated_by": navigation_controller.updated_by,
        }
