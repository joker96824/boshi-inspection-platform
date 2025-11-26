"""
云台预设点业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.gimbalpresetpoint_repository import GimbalPresetPointRepository
from ..repositories.gimbal_repository import GimbalRepository
from ..schemas.gimbalpresetpoint import (
    GimbalPresetPointCreate,
    GimbalPresetPointUpdate,
    GimbalPresetPointQuery,
)
from ..core.exceptions import (
    ResourceNotFoundError,
    BusinessError,
    ValidationError,
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalPresetPointService:
    """云台预设点业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.preset_point_repo = GimbalPresetPointRepository(db)
        self.gimbal_repo = GimbalRepository(db)

    async def create_preset_point(
        self, preset_point_data: GimbalPresetPointCreate, user: dict
    ) -> Dict[str, Any]:
        """创建云台预设点"""
        try:
            # 检查云台是否存在
            gimbal = await self.gimbal_repo.get_by_id(preset_point_data.gimbal_id)
            if not gimbal:
                raise ResourceNotFoundError(
                    f"云台ID '{preset_point_data.gimbal_id}' 不存在"
                )

            # 检查预设点名称是否已存在（同一云台下）
            if await self.preset_point_repo.exists_by_name(
                preset_point_data.preset_name,
                preset_point_data.gimbal_id,
            ):
                raise BusinessError(
                    f"预设点名称 '{preset_point_data.preset_name}' 在该云台下已存在"
                )

            create_data = preset_point_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            preset_point = await self.preset_point_repo.create(create_data)

            log_user_action(
                user["username"],
                "create_gimbal_preset_point",
                "success",
                f"创建云台预设点成功，ID: {preset_point.id}",
            )

            return ApiResponse.success(
                data=self._format_preset_point_response(preset_point),
                message="创建云台预设点成功",
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"创建云台预设点失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
            if "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建云台预设点失败-唯一性约束错误: {error_msg}")
                raise BusinessError(
                    f"预设点名称 '{preset_point_data.preset_name}' 在该云台下已存在"
                )
            elif "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台预设点失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台不存在，请检查云台ID是否正确")
            else:
                logger.error(f"创建云台预设点失败-数据库完整性错误: {error_msg}")
                raise BusinessError("数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台预设点失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台预设点失败: {str(e)}")

    async def get_preset_point_by_id(
        self, preset_point_id: str, user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID获取云台预设点"""
        try:
            preset_point = await self.preset_point_repo.get_by_id(preset_point_id)
            if not preset_point:
                raise ResourceNotFoundError(
                    f"云台预设点ID '{preset_point_id}' 不存在"
                )

            return ApiResponse.success(
                data=self._format_preset_point_response(preset_point),
                message="获取云台预设点成功",
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取云台预设点失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台预设点失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台预设点失败: {str(e)}")

    async def get_preset_points_by_ids(
        self, preset_point_ids: List[str], user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID列表获取云台预设点"""
        try:
            preset_points = await self.preset_point_repo.get_by_ids(preset_point_ids)

            preset_points_data = [
                self._format_preset_point_response(pp) for pp in preset_points
            ]

            return ApiResponse.success(
                data={
                    "preset_points": preset_points_data,
                    "total": len(preset_points_data),
                },
                message="获取云台预设点列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台预设点列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台预设点列表失败: {str(e)}")

    async def get_preset_points(
        self, query: GimbalPresetPointQuery, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取云台预设点列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                preset_points, total = await self.preset_point_repo.get_all(
                    page=None,
                    size=None,
                    preset_name=query.preset_name,
                    gimbal_id=query.gimbal_id,
                    sort_by=query.sort_by,
                    sort_order=query.sort_order,
                )
                preset_points_data = [
                    self._format_preset_point_response(pp) for pp in preset_points
                ]
                return ApiResponse.success(
                    data={"items": preset_points_data, "total": total},
                    message="获取云台预设点列表成功",
                )

            preset_points, total = await self.preset_point_repo.get_all(
                page=query.page,
                size=query.size,
                preset_name=query.preset_name,
                gimbal_id=query.gimbal_id,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
            )

            # 格式化响应数据
            preset_points_data = [
                self._format_preset_point_response(pp) for pp in preset_points
            ]

            return ApiResponse.paginated(
                items=preset_points_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台预设点列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台预设点列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台预设点列表失败: {str(e)}")

    async def update_preset_point(
        self,
        preset_point_id: str,
        preset_point_data: GimbalPresetPointUpdate,
        user: dict,
    ) -> Dict[str, Any]:
        """更新云台预设点"""
        try:
            # 检查预设点是否存在
            existing_preset_point = await self.preset_point_repo.get_by_id(
                preset_point_id
            )
            if not existing_preset_point:
                raise ResourceNotFoundError(
                    f"云台预设点ID '{preset_point_id}' 不存在"
                )

            # 如果更新了名称，检查是否重复
            target_gimbal_id = (
                existing_preset_point.gimbal_id
            )  # 预设点不能更换云台
            if (
                preset_point_data.preset_name
                and preset_point_data.preset_name != existing_preset_point.preset_name
                and await self.preset_point_repo.exists_by_name(
                    preset_point_data.preset_name, target_gimbal_id, preset_point_id
                )
            ):
                raise BusinessError(
                    f"预设点名称 '{preset_point_data.preset_name}' 在该云台下已存在"
                )

            update_data = preset_point_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]

            updated_preset_point = await self.preset_point_repo.update(
                preset_point_id, update_data
            )

            log_user_action(
                user["username"],
                "update_gimbal_preset_point",
                "success",
                f"更新云台预设点成功，ID: {preset_point_id}",
            )

            return ApiResponse.success(
                data=self._format_preset_point_response(updated_preset_point),
                message="更新云台预设点成功",
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"更新云台预设点失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台预设点失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台预设点失败: {str(e)}")

    async def delete_preset_point(
        self, preset_point_id: str, user: dict
    ) -> Dict[str, Any]:
        """删除云台预设点"""
        try:
            # 检查预设点是否存在
            existing_preset_point = await self.preset_point_repo.get_by_id(
                preset_point_id
            )
            if not existing_preset_point:
                raise ResourceNotFoundError(
                    f"云台预设点ID '{preset_point_id}' 不存在"
                )

            # 删除预设点
            success = await self.preset_point_repo.soft_delete(
                preset_point_id, user["username"]
            )

            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal_preset_point",
                    "success",
                    f"删除云台预设点成功，ID: {preset_point_id}",
                )

                return ApiResponse.success(
                    data={"id": preset_point_id}, message="删除云台预设点成功"
                )
            else:
                raise BusinessError("删除云台预设点失败")

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"删除云台预设点失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台预设点失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台预设点失败: {str(e)}")

    async def get_preset_point_stats(
        self, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取云台预设点统计信息"""
        try:
            total_count = await self.preset_point_repo.count_all()

            stats = {"total_preset_points": total_count}

            return ApiResponse.success(
                data=stats, message="获取云台预设点统计成功"
            )

        except Exception as e:
            logger.error(f"获取云台预设点统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台预设点统计失败: {str(e)}")

    def _format_preset_point_response(
        self, preset_point
    ) -> Dict[str, Any]:
        """格式化云台预设点响应数据"""
        gimbal_info = None
        if preset_point.gimbal:
            gimbal_info = {
                "id": preset_point.gimbal.id,
                "gimbal_name": preset_point.gimbal.gimbal_name,
                "map_id": preset_point.gimbal.map_id,
            }

        return {
            "id": preset_point.id,
            "preset_name": preset_point.preset_name,
            "gimbal_id": preset_point.gimbal_id,
            "p_coordinate": preset_point.p_coordinate,
            "t_coordinate": preset_point.t_coordinate,
            "z_coordinate": preset_point.z_coordinate,
            "f_coordinate": preset_point.f_coordinate,
            "aperture": preset_point.aperture,
            "shutter": preset_point.shutter,
            "backlight_compensation": preset_point.backlight_compensation,
            "wide_dynamic": preset_point.wide_dynamic,
            "strong_light_suppression": preset_point.strong_light_suppression,
            "fill_light": preset_point.fill_light,
            "image_url": preset_point.image_url,
            "gimbal": gimbal_info,
            "created_at": preset_point.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            if preset_point.created_at
            else None,
            "updated_at": preset_point.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            if preset_point.updated_at
            else None,
            "created_by": preset_point.created_by,
            "updated_by": preset_point.updated_by,
        }

