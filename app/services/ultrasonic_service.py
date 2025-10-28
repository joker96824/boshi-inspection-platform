"""
超声波状态配置业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.ultrasonic_repository import UltrasonicRepository
from ..schemas.ultrasonic import UltrasonicCreate, UltrasonicUpdate, UltrasonicQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class UltrasonicService:
    """超声波状态配置业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = UltrasonicRepository(db)

    async def create_ultrasonic(self, data: UltrasonicCreate, user: dict) -> Dict[str, Any]:
        """创建超声波状态配置"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建超声波状态配置
            ultrasonic = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_ultrasonic",
                f"创建超声波状态配置: ID{ultrasonic.ultrasonic_id}, 波特率{ultrasonic.baud_rate}",
                extra={"ultrasonic_id": ultrasonic.id, "ultrasonic_id_value": ultrasonic.ultrasonic_id, "baud_rate": ultrasonic.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_ultrasonic_response(ultrasonic),
                message="超声波状态配置创建成功"
            )

        except Exception as e:
            logger.error(f"创建超声波状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"创建超声波状态配置失败: {str(e)}")

    async def get_ultrasonic_by_id(self, ultrasonic_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取超声波状态配置"""
        try:
            ultrasonic = await self.repo.get_by_id(ultrasonic_id)
            if not ultrasonic:
                raise ResourceNotFoundError(f"超声波状态配置ID '{ultrasonic_id}' 不存在")

            return ApiResponse.success(
                data=self._format_ultrasonic_response(ultrasonic),
                message="获取超声波状态配置成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取超声波状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"获取超声波状态配置失败: {str(e)}")

    async def get_ultrasonics_by_ids(self, ultrasonic_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取超声波状态配置"""
        try:
            ultrasonics = await self.repo.get_by_ids(ultrasonic_ids)
            if not ultrasonics:
                raise ResourceNotFoundError("未找到任何超声波状态配置")

            return ApiResponse.success(
                data=[self._format_ultrasonic_response(ultrasonic) for ultrasonic in ultrasonics],
                message=f"成功获取 {len(ultrasonics)} 个超声波状态配置"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取超声波状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取超声波状态配置失败: {str(e)}")

    async def get_ultrasonics(self, query: UltrasonicQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取超声波状态配置列表"""
        try:
            ultrasonics, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                ultrasonic_id=query.ultrasonic_id,
                baud_rate=query.baud_rate,
                obstacle_avoidance_distance_min=query.obstacle_avoidance_distance_min,
                obstacle_avoidance_distance_max=query.obstacle_avoidance_distance_max
            )

            return ApiResponse.paginated(
                items=[self._format_ultrasonic_response(ultrasonic) for ultrasonic in ultrasonics],
                total=total,
                page=query.page,
                size=query.size,
                message="获取超声波状态配置列表成功"
            )

        except Exception as e:
            logger.error(f"获取超声波状态配置列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取超声波状态配置列表失败: {str(e)}")

    async def update_ultrasonic(self, ultrasonic_id: str, data: UltrasonicUpdate, user: dict) -> Dict[str, Any]:
        """更新超声波状态配置"""
        try:
            # 检查超声波状态配置是否存在
            existing_ultrasonic = await self.repo.get_by_id(ultrasonic_id)
            if not existing_ultrasonic:
                raise ResourceNotFoundError(f"超声波状态配置ID '{ultrasonic_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新超声波状态配置
            ultrasonic = await self.repo.update(ultrasonic_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_ultrasonic",
                f"更新超声波状态配置: ID{ultrasonic.ultrasonic_id}, 波特率{ultrasonic.baud_rate}",
                extra={"ultrasonic_id": ultrasonic.id, "ultrasonic_id_value": ultrasonic.ultrasonic_id, "baud_rate": ultrasonic.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_ultrasonic_response(ultrasonic),
                message="超声波状态配置更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新超声波状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"更新超声波状态配置失败: {str(e)}")

    async def delete_ultrasonic(self, ultrasonic_id: str, user: dict) -> Dict[str, Any]:
        """删除超声波状态配置"""
        try:
            # 检查超声波状态配置是否存在
            existing_ultrasonic = await self.repo.get_by_id(ultrasonic_id)
            if not existing_ultrasonic:
                raise ResourceNotFoundError(f"超声波状态配置ID '{ultrasonic_id}' 不存在")

            # 软删除超声波状态配置
            success = await self.repo.soft_delete(ultrasonic_id, user["username"])
            if not success:
                raise BusinessError(f"删除超声波状态配置失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_ultrasonic",
                f"删除超声波状态配置: ID{existing_ultrasonic.ultrasonic_id}, 波特率{existing_ultrasonic.baud_rate}",
                extra={"ultrasonic_id": ultrasonic_id, "ultrasonic_id_value": existing_ultrasonic.ultrasonic_id, "baud_rate": existing_ultrasonic.baud_rate}
            )

            return ApiResponse.success(
                data={"id": ultrasonic_id},
                message="超声波状态配置删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除超声波状态配置失败: {e}", exc_info=True)
            raise BusinessError(f"删除超声波状态配置失败: {str(e)}")

    async def get_ultrasonic_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取超声波状态配置统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取超声波状态配置统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取超声波状态配置统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取超声波状态配置统计信息失败: {str(e)}")

    def _format_ultrasonic_response(self, ultrasonic) -> Dict[str, Any]:
        """格式化超声波状态配置响应数据"""
        return {
            "id": ultrasonic.id,
            "ultrasonic_id": ultrasonic.ultrasonic_id,
            "obstacle_avoidance_distance": float(ultrasonic.obstacle_avoidance_distance) if ultrasonic.obstacle_avoidance_distance else 0.0,
            "deceleration_distance": float(ultrasonic.deceleration_distance) if ultrasonic.deceleration_distance else 0.0,
            "baud_rate": ultrasonic.baud_rate,
            "created_at": ultrasonic.created_at.strftime("%Y-%m-%dT%H:%M:%S") if ultrasonic.created_at else None,
            "updated_at": ultrasonic.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if ultrasonic.updated_at else None,
            "created_by": ultrasonic.created_by,
            "updated_by": ultrasonic.updated_by,
        }
