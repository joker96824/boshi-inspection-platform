"""
深度相机配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.depthcamera_repository import DepthCameraRepository
from ..schemas.depthcamera import DepthCameraCreate, DepthCameraUpdate, DepthCameraQuery, DepthCameraBatchUpdate
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class DepthCameraService:
    """深度相机配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DepthCameraRepository(db)

    async def create_depth_camera(self, data: DepthCameraCreate, user: dict) -> Dict[str, Any]:
        """创建深度相机配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建深度相机配置
            depth_camera = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_depth_camera",
                f"创建深度相机配置: 串口ID{depth_camera.serial_port_id}",
                extra={"camera_id": depth_camera.id, "serial_port_id": depth_camera.serial_port_id}
            )

            return ApiResponse.success(
                data=self._format_camera_response(depth_camera),
                message="深度相机配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建深度相机配置失败: {str(e)}")

    async def get_depth_camera_by_id(self, camera_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取深度相机配置"""
        try:
            depth_camera = await self.repo.get_by_id(camera_id)
            if not depth_camera:
                raise ResourceNotFoundError(f"深度相机配置ID '{camera_id}' 不存在")

            return ApiResponse.success(
                data=self._format_camera_response(depth_camera),
                message="获取深度相机配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取深度相机配置失败: {str(e)}")

    async def get_depth_cameras_by_ids(self, depthcamera_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取深度相机配置"""
        try:
            depth_cameras = await self.repo.get_by_ids(depthcamera_ids)
            if not depth_cameras:
                raise ResourceNotFoundError("未找到任何深度相机配置")

            return ApiResponse.success(
                data=[self._format_camera_response(camera) for camera in depth_cameras],
                message=f"成功获取 {len(depth_cameras)} 个深度相机配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取深度相机配置失败: {str(e)}")

    async def get_depth_cameras(self, query: DepthCameraQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取深度相机配置列表"""
        try:
            depth_cameras, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                serial_port_id=query.serial_port_id,
                camera_mode=query.camera_mode
            )

            return ApiResponse.paginated(
                items=[self._format_camera_response(camera) for camera in depth_cameras],
                total=total,
                page=query.page,
                size=query.size,
                message="获取深度相机配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取深度相机配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取深度相机配置列表失败: {str(e)}")

    async def update_depth_camera(self, camera_id: str, data: DepthCameraUpdate, user: dict) -> Dict[str, Any]:
        """更新深度相机配置（单个，兼容旧接口）"""
        try:
            # 检查深度相机配置是否存在
            existing_camera = await self.repo.get_by_id(camera_id)
            if not existing_camera:
                raise ResourceNotFoundError(f"深度相机配置ID '{camera_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新深度相机配置
            depth_camera = await self.repo.update(camera_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_depth_camera",
                f"更新深度相机配置: 串口ID{depth_camera.serial_port_id}",
                extra={"camera_id": depth_camera.id, "serial_port_id": depth_camera.serial_port_id}
            )

            return ApiResponse.success(
                data=self._format_camera_response(depth_camera),
                message="深度相机配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新深度相机配置失败: {str(e)}")
    
    async def batch_update_depth_cameras_by_robot(self, robot_id: str, configs: List[DepthCameraCreate], user: dict) -> Dict[str, Any]:
        """批量更新机器人的深度相机配置（真删除旧数据后重新添加）"""
        try:
            from ..repositories.robot_repository import RobotRepository
            # 检查机器人是否存在
            robot_repo = RobotRepository(self.db)
            robot = await robot_repo.get_by_id(robot_id)
            if not robot:
                raise ResourceNotFoundError(f"机器人ID '{robot_id}' 不存在")
            
            # 真删除该机器人的所有旧配置
            deleted_count = await self.repo.hard_delete_by_robot_id(robot_id)
            logger.info(f"删除机器人 {robot_id} 的 {deleted_count} 个旧深度相机配置")
            
            # 创建新配置
            created_configs = []
            for config_data in configs:
                create_data = {
                    **config_data.dict(),
                    "robot_id": robot_id,
                    "created_by": user["username"],
                    "updated_by": user["username"]
                }
                depth_camera = await self.repo.create(create_data)
                created_configs.append(depth_camera)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "batch_update_depth_cameras",
                f"批量更新机器人 {robot_id} 的深度相机配置: 删除{deleted_count}个，新增{len(created_configs)}个",
                extra={"robot_id": robot_id, "deleted_count": deleted_count, "created_count": len(created_configs)}
            )

            return ApiResponse.success(
                data=[self._format_camera_response(config) for config in created_configs],
                message=f"批量更新深度相机配置成功，删除{deleted_count}个，新增{len(created_configs)}个"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量更新深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量更新深度相机配置失败: {str(e)}")

    async def delete_depth_camera(self, camera_id: str, user: dict) -> Dict[str, Any]:
        """删除深度相机配置"""
        try:
            # 检查深度相机配置是否存在
            existing_camera = await self.repo.get_by_id(camera_id)
            if not existing_camera:
                raise ResourceNotFoundError(f"深度相机配置ID '{camera_id}' 不存在")

            # 软删除深度相机配置
            success = await self.repo.soft_delete(camera_id, user["username"])
            if not success:
                raise BusinessError(f"删除深度相机配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_depth_camera",
                f"删除深度相机配置: 串口ID{existing_camera.serial_port_id}",
                extra={"camera_id": camera_id, "serial_port_id": existing_camera.serial_port_id}
            )

            return ApiResponse.success(
                data={"id": camera_id},
                message="深度相机配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除深度相机配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除深度相机配置失败: {str(e)}")

    async def get_depth_camera_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取深度相机配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取深度相机配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取深度相机配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取深度相机配置统计信息失败: {str(e)}")

    def _format_camera_response(self, depth_camera) -> Dict[str, Any]:
        """格式化深度相机配置响应数据"""
        return {
            "id": depth_camera.id,
            "robot_id": depth_camera.robot_id,
            "serial_port_id": depth_camera.serial_port_id,
            "camera_mode": depth_camera.camera_mode,
            "image_flip": depth_camera.image_flip,
            "image_alignment": depth_camera.image_alignment,
            "created_at": depth_camera.created_at.strftime("%Y-%m-%dT%H:%M:%S") if depth_camera.created_at else None,
            "updated_at": depth_camera.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if depth_camera.updated_at else None,
            "created_by": depth_camera.created_by,
            "updated_by": depth_camera.updated_by,
        }
