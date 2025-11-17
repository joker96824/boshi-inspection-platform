"""
云台巡检项目业务逻辑服务
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.logging import get_logger, log_user_action
from ..core.exceptions import BusinessError, ResourceNotFoundError, ValidationError
from ..repositories.gimbalinspectionproject_repository import (
    GimbalInspectionProjectRepository,
)
from ..repositories.gimbaltask_repository import GimbalTaskRepository
from ..schemas.gimbalinspectionproject import (
    GimbalInspectionProjectCreate,
    GimbalInspectionProjectQuery,
    GimbalInspectionProjectUpdate,
)
from ..utils.response import ApiResponse

logger = get_logger(__name__)


class GimbalInspectionProjectService:
    """云台巡检项目业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.project_repo = GimbalInspectionProjectRepository(db)
        self.gimbal_task_repo = GimbalTaskRepository(db)

    async def create_project(
        self, project_data: GimbalInspectionProjectCreate, user: dict
    ) -> Dict[str, Any]:
        """创建云台巡检项目"""
        try:
            task = await self.gimbal_task_repo.get_by_id(project_data.gimbaltask_id)
            if not task:
                raise ResourceNotFoundError(
                    f"云台任务ID '{project_data.gimbaltask_id}' 不存在"
                )

            if await self.project_repo.exists_by_name(
                project_data.task_name, project_data.gimbaltask_id
            ):
                raise BusinessError(
                    f"巡检项目名称 '{project_data.task_name}' 在该云台任务下已存在"
                )

            create_data = project_data.dict()
            if create_data.get("sort_order") is None:
                create_data["sort_order"] = await self.project_repo.get_next_sort_order(
                    project_data.gimbaltask_id
                )
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            project = await self.project_repo.create(create_data)

            log_user_action(
                user["username"],
                "create_gimbal_inspection_project",
                "success",
                f"创建云台巡检项目成功，ID: {project.id}",
            )

            return ApiResponse.success(
                data=self._format_project_response(project), message="创建云台巡检项目成功"
            )

        except (ValidationError, ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台巡检项目失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
            if "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建云台巡检项目失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"巡检项目名称 '{project_data.task_name}' 已存在")
            elif "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台巡检项目失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台任务不存在，请检查云台任务ID是否正确")
            else:
                logger.error(f"创建云台巡检项目失败-数据库完整性错误: {error_msg}")
                raise BusinessError("数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台巡检项目失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台巡检项目失败: {str(e)}")

    async def get_project_by_id(
        self, project_id: str, user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID获取巡检项目"""
        try:
            project = await self.project_repo.get_by_id(project_id)
            if not project:
                raise ResourceNotFoundError(f"云台巡检项目ID '{project_id}' 不存在")

            return ApiResponse.success(
                data=self._format_project_response(project), message="获取巡检项目成功"
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取云台巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台巡检项目失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检项目失败: {str(e)}")

    async def get_projects_by_ids(
        self, project_ids: List[str], user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID列表获取巡检项目"""
        try:
            projects = await self.project_repo.get_by_ids(project_ids)
            projects_data = [self._format_project_response(project) for project in projects]

            return ApiResponse.success(
                data={"inspection_projects": projects_data, "total": len(projects_data)},
                message="获取云台巡检项目列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台巡检项目列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检项目列表失败: {str(e)}")

    async def get_projects(
        self, query: GimbalInspectionProjectQuery, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取巡检项目列表"""
        try:
            projects, total = await self.project_repo.get_all(
                page=query.page,
                size=query.size,
                task_name=query.task_name,
                gimbaltask_id=query.gimbaltask_id,
                gimbal_id=query.gimbal_id,
                map_id=query.map_id,
            )

            projects_data = [self._format_project_response(project) for project in projects]

            return ApiResponse.paginated(
                items=projects_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台巡检项目列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台巡检项目列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检项目列表失败: {str(e)}")

    async def update_project(
        self, project_id: str, project_data: GimbalInspectionProjectUpdate, user: dict
    ) -> Dict[str, Any]:
        """更新巡检项目"""
        try:
            existing_project = await self.project_repo.get_by_id(project_id)
            if not existing_project:
                raise ResourceNotFoundError(f"云台巡检项目ID '{project_id}' 不存在")

            target_task_id = project_data.gimbaltask_id or existing_project.gimbaltask_id
            if project_data.gimbaltask_id and project_data.gimbaltask_id != existing_project.gimbaltask_id:
                task = await self.gimbal_task_repo.get_by_id(project_data.gimbaltask_id)
                if not task:
                    raise ResourceNotFoundError(
                        f"云台任务ID '{project_data.gimbaltask_id}' 不存在"
                    )

            if (
                project_data.task_name
                and await self.project_repo.exists_by_name(
                    project_data.task_name,
                    target_task_id,
                    project_id,
                )
            ):
                raise BusinessError(
                    f"巡检项目名称 '{project_data.task_name}' 在该云台任务下已存在"
                )

            update_data = project_data.dict(exclude_unset=True)
            if (
                "sort_order" in update_data
                and update_data["sort_order"] is None
            ):
                raise ValidationError("排序值不能为空")

            if (
                "gimbaltask_id" in update_data
                and update_data["gimbaltask_id"] != existing_project.gimbaltask_id
                and "sort_order" not in update_data
            ):
                update_data["sort_order"] = await self.project_repo.get_next_sort_order(
                    update_data["gimbaltask_id"]
                )

            update_data["updated_by"] = user["username"]

            updated_project = await self.project_repo.update(project_id, update_data)

            log_user_action(
                user["username"],
                "update_gimbal_inspection_project",
                "success",
                f"更新云台巡检项目成功，ID: {project_id}",
            )

            return ApiResponse.success(
                data=self._format_project_response(updated_project),
                message="更新云台巡检项目成功",
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"更新云台巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台巡检项目失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台巡检项目失败: {str(e)}")

    async def delete_project(self, project_id: str, user: dict) -> Dict[str, Any]:
        """删除巡检项目"""
        try:
            existing_project = await self.project_repo.get_by_id(project_id)
            if not existing_project:
                raise ResourceNotFoundError(f"云台巡检项目ID '{project_id}' 不存在")

            success = await self.project_repo.soft_delete(
                project_id, user["username"]
            )

            if not success:
                raise BusinessError("删除云台巡检项目失败")

            log_user_action(
                user["username"],
                "delete_gimbal_inspection_project",
                "success",
                f"删除云台巡检项目成功，ID: {project_id}",
            )

            return ApiResponse.success(
                data={"project_id": project_id}, message="删除云台巡检项目成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"删除云台巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台巡检项目失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台巡检项目失败: {str(e)}")

    async def get_project_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取巡检项目统计信息"""
        try:
            total_count = await self.project_repo.count_all()

            return ApiResponse.success(
                data={"total_inspection_projects": total_count},
                message="获取云台巡检项目统计成功",
            )

        except Exception as e:
            logger.error(f"获取云台巡检项目统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台巡检项目统计失败: {str(e)}")

    def _format_project_response(self, project) -> Dict[str, Any]:
        """格式化巡检项目响应数据"""
        task_info = None
        if project.gimbal_task:
            task_info = {
                "id": project.gimbal_task.id,
                "task_name": project.gimbal_task.task_name,
                "gimbal_id": project.gimbal_task.gimbal_id,
            }

        # 格式化预设点关联信息
        preset_points_info = []
        if hasattr(project, 'preset_points') and project.preset_points:
            active_preset_points = [pp for pp in project.preset_points if not pp.is_deleted]
            for pp_link in active_preset_points:
                preset_point = pp_link.preset_point if hasattr(pp_link, 'preset_point') else None
                if preset_point and not preset_point.is_deleted:
                    preset_points_info.append({
                        "id": preset_point.id,
                        "preset_name": preset_point.preset_name,
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
                        "detection_type": pp_link.detection_type,
                        "video_duration": pp_link.video_duration,
                        "created_at": preset_point.created_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.created_at else None,
                        "updated_at": preset_point.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if preset_point.updated_at else None,
                    })

        return {
            "id": project.id,
            "task_name": project.task_name,
            "gimbaltask_id": project.gimbaltask_id,
            "sort_order": project.sort_order,
            "preset_points": preset_points_info,
            "gimbal_task": task_info,
            "created_at": project.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            if project.created_at
            else None,
            "updated_at": project.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            if project.updated_at
            else None,
            "created_by": project.created_by,
            "updated_by": project.updated_by,
        }

