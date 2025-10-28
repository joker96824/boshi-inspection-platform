"""
激光雷达配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.lidar_repository import LidarRepository
from ..schemas.lidar import LidarCreate, LidarUpdate, LidarQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class LidarService:
    """激光雷达配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = LidarRepository(db)

    async def create_lidar(self, data: LidarCreate, user: dict) -> Dict[str, Any]:
        """创建激光雷达配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建激光雷达配置
            lidar = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_lidar",
                f"创建激光雷达配置: IP{lidar.lidar_ip}, 端口{lidar.lidar_port}",
                extra={"lidar_id": lidar.id, "lidar_ip": lidar.lidar_ip, "lidar_port": lidar.lidar_port}
            )

            return ApiResponse.success(
                data=self._format_lidar_response(lidar),
                message="激光雷达配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建激光雷达配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建激光雷达配置失败: {str(e)}")

    async def get_lidar_by_id(self, lidar_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取激光雷达配置"""
        try:
            lidar = await self.repo.get_by_id(lidar_id)
            if not lidar:
                raise ResourceNotFoundError(f"激光雷达配置ID '{lidar_id}' 不存在")

            return ApiResponse.success(
                data=self._format_lidar_response(lidar),
                message="获取激光雷达配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取激光雷达配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取激光雷达配置失败: {str(e)}")

    async def get_lidars_by_ids(self, lidar_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取激光雷达配置"""
        try:
            lidars = await self.repo.get_by_ids(lidar_ids)
            if not lidars:
                raise ResourceNotFoundError("未找到任何激光雷达配置")

            return ApiResponse.success(
                data=[self._format_lidar_response(lidar) for lidar in lidars],
                message=f"成功获取 {len(lidars)} 个激光雷达配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取激光雷达配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取激光雷达配置失败: {str(e)}")

    async def get_lidars(self, query: LidarQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取激光雷达配置列表"""
        try:
            lidars, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                lidar_ip=query.lidar_ip,
                lidar_port=query.lidar_port,
                scan_frequency_rpm=query.scan_frequency_rpm
            )

            return ApiResponse.paginated(
                items=[self._format_lidar_response(lidar) for lidar in lidars],
                total=total,
                page=query.page,
                size=query.size,
                message="获取激光雷达配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取激光雷达配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取激光雷达配置列表失败: {str(e)}")

    async def update_lidar(self, lidar_id: str, data: LidarUpdate, user: dict) -> Dict[str, Any]:
        """更新激光雷达配置"""
        try:
            # 检查激光雷达配置是否存在
            existing_lidar = await self.repo.get_by_id(lidar_id)
            if not existing_lidar:
                raise ResourceNotFoundError(f"激光雷达配置ID '{lidar_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新激光雷达配置
            lidar = await self.repo.update(lidar_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_lidar",
                f"更新激光雷达配置: IP{lidar.lidar_ip}, 端口{lidar.lidar_port}",
                extra={"lidar_id": lidar.id, "lidar_ip": lidar.lidar_ip, "lidar_port": lidar.lidar_port}
            )

            return ApiResponse.success(
                data=self._format_lidar_response(lidar),
                message="激光雷达配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新激光雷达配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新激光雷达配置失败: {str(e)}")

    async def delete_lidar(self, lidar_id: str, user: dict) -> Dict[str, Any]:
        """删除激光雷达配置"""
        try:
            # 检查激光雷达配置是否存在
            existing_lidar = await self.repo.get_by_id(lidar_id)
            if not existing_lidar:
                raise ResourceNotFoundError(f"激光雷达配置ID '{lidar_id}' 不存在")

            # 软删除激光雷达配置
            success = await self.repo.soft_delete(lidar_id, user["username"])
            if not success:
                raise BusinessError(f"删除激光雷达配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_lidar",
                f"删除激光雷达配置: IP{existing_lidar.lidar_ip}, 端口{existing_lidar.lidar_port}",
                extra={"lidar_id": lidar_id, "lidar_ip": existing_lidar.lidar_ip, "lidar_port": existing_lidar.lidar_port}
            )

            return ApiResponse.success(
                data={"id": lidar_id},
                message="激光雷达配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除激光雷达配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除激光雷达配置失败: {str(e)}")

    async def get_lidar_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取激光雷达配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取激光雷达配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取激光雷达配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取激光雷达配置统计信息失败: {str(e)}")

    def _format_lidar_response(self, lidar) -> Dict[str, Any]:
        """格式化激光雷达配置响应数据"""
        return {
            "id": lidar.id,
            "lidar_ip": lidar.lidar_ip,
            "subnet_mask": lidar.subnet_mask,
            "gateway": lidar.gateway,
            "lidar_port": lidar.lidar_port,
            "scan_frequency_rpm": lidar.scan_frequency_rpm,
            "x_coordinate": float(lidar.x_coordinate) if lidar.x_coordinate else 0.0,
            "y_coordinate": float(lidar.y_coordinate) if lidar.y_coordinate else 0.0,
            "z_coordinate": float(lidar.z_coordinate) if lidar.z_coordinate else 0.0,
            "scan_range_min": float(lidar.scan_range_min) if lidar.scan_range_min else 0.0,
            "scan_range_max": float(lidar.scan_range_max) if lidar.scan_range_max else 0.0,
            "scan_distance_min": float(lidar.scan_distance_min) if lidar.scan_distance_min else 0.0,
            "scan_distance_max": float(lidar.scan_distance_max) if lidar.scan_distance_max else 0.0,
            "created_at": lidar.created_at.strftime("%Y-%m-%dT%H:%M:%S") if lidar.created_at else None,
            "updated_at": lidar.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if lidar.updated_at else None,
            "created_by": lidar.created_by,
            "updated_by": lidar.updated_by,
        }
