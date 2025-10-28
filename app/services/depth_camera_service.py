"""
深度相机配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.depthcamera_repository import DepthCameraRepository
from ..schemas.depthcamera import DepthCameraCreate, DepthCameraUpdate, DepthCameraQuery
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
                f"创建深度相机配置: 类型{depth_camera.camera_type}",
                extra={"camera_id": depth_camera.id, "camera_type": depth_camera.camera_type}
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
                camera_type=query.camera_type,
                protocol=query.protocol,
                frame_rate=query.frame_rate,
                camera_ip=query.camera_ip
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
        """更新深度相机配置"""
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
                f"更新深度相机配置: 类型{depth_camera.camera_type}",
                extra={"camera_id": depth_camera.id, "camera_type": depth_camera.camera_type}
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
                f"删除深度相机配置: 类型{existing_camera.camera_type}",
                extra={"camera_id": camera_id, "camera_type": existing_camera.camera_type}
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
            "camera_type": depth_camera.camera_type,
            "resolution_width": depth_camera.resolution_width,
            "resolution_height": depth_camera.resolution_height,
            "frame_rate": depth_camera.frame_rate,
            "depth_range_min": float(depth_camera.depth_range_min) if depth_camera.depth_range_min else 0.0,
            "depth_range_max": float(depth_camera.depth_range_max) if depth_camera.depth_range_max else 0.0,
            "depth_accuracy": float(depth_camera.depth_accuracy) if depth_camera.depth_accuracy else 0.0,
            "camera_ip": depth_camera.camera_ip,
            "camera_port": depth_camera.camera_port,
            "protocol": depth_camera.protocol,
            "exposure_time": depth_camera.exposure_time,
            "gain": float(depth_camera.gain) if depth_camera.gain else None,
            "white_balance": depth_camera.white_balance,
            "created_at": depth_camera.created_at.strftime("%Y-%m-%dT%H:%M:%S") if depth_camera.created_at else None,
            "updated_at": depth_camera.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if depth_camera.updated_at else None,
            "created_by": depth_camera.created_by,
            "updated_by": depth_camera.updated_by,
        }
