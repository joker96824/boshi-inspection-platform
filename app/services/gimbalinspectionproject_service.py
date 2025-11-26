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
from ..repositories.gimbalinspectionprojectpresetpoint_repository import (
    GimbalInspectionProjectPresetPointRepository,
)
from ..repositories.gimbalpresetpoint_repository import GimbalPresetPointRepository
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
        self.link_repo = GimbalInspectionProjectPresetPointRepository(db)
        self.preset_point_repo = GimbalPresetPointRepository(db)

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
            for pp_link in project.preset_points:
                preset_point = pp_link.preset_point if hasattr(pp_link, 'preset_point') else None
                if preset_point:
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

    async def set_project_preset_points(
        self,
        inspection_project_id: str,
        preset_point_links: List[Dict[str, Any]],
        user: dict,
    ) -> Dict[str, Any]:
        """设置巡检项目的预设点关联（删除原有关联，添加新关联）

        Args:
            inspection_project_id: 巡检项目ID
            preset_point_links: 预设点关联列表，每个关联包含：
                - preset_point_id: 预设点ID
                - detection_type: 检测类型
                - video_duration: 视频时长（可选，当detection_type为视频类型时使用）

        Returns:
            设置结果
        """
        try:
            # 检查巡检项目是否存在
            project = await self.project_repo.get_by_id(inspection_project_id)
            if not project:
                raise ResourceNotFoundError(
                    f"云台巡检项目ID '{inspection_project_id}' 不存在"
                )

            # 验证预设点是否存在
            preset_point_ids = [link["preset_point_id"] for link in preset_point_links]
            if preset_point_ids:
                preset_points = await self.preset_point_repo.get_by_ids(preset_point_ids)
                found_ids = {pp.id for pp in preset_points}
                missing_ids = set(preset_point_ids) - found_ids
                if missing_ids:
                    raise ResourceNotFoundError(
                        f"预设点ID不存在: {', '.join(missing_ids)}"
                    )

            # 验证检测类型
            valid_detection_types = [
                "可见光图片",
                "可见光视频",
                "热成像图片",
                "热成像视频",
            ]
            for link in preset_point_links:
                if link.get("detection_type") not in valid_detection_types:
                    raise ValidationError(
                        f"检测类型 '{link.get('detection_type')}' 无效，必须是: {', '.join(valid_detection_types)}"
                    )
                # 如果是视频类型，必须提供video_duration
                if link.get("detection_type") in ["可见光视频", "热成像视频"]:
                    if not link.get("video_duration"):
                        raise ValidationError(
                            f"检测类型为 '{link.get('detection_type')}' 时，必须提供 video_duration"
                        )

            # 检查是否有重复的 (preset_point_id, detection_type) 组合
            seen_combinations = set()
            for link in preset_point_links:
                combination = (link["preset_point_id"], link["detection_type"])
                if combination in seen_combinations:
                    raise ValidationError(
                        f"预设点关联中存在重复的组合：预设点ID '{link['preset_point_id']}' 和检测类型 '{link['detection_type']}'"
                    )
                seen_combinations.add(combination)

            # 获取所有旧关联
            old_links = await self.link_repo.get_by_inspection_project_id(
                inspection_project_id
            )
            old_links_map = {
                (link.preset_point_id, link.detection_type): link
                for link in old_links
            }

            # 处理新关联：更新已存在的或创建新的
            links_to_create = []
            links_to_update = []

            for link in preset_point_links:
                combination = (link["preset_point_id"], link["detection_type"])
                if combination in old_links_map:
                    # 如果已存在，更新它
                    existing_link = old_links_map[combination]
                    existing_link.video_duration = link.get("video_duration")
                    existing_link.updated_by = user["username"]
                    links_to_update.append(existing_link)
                else:
                    # 创建新关联
                    link_data = {
                        "inspection_project_id": inspection_project_id,
                        "preset_point_id": link["preset_point_id"],
                        "detection_type": link["detection_type"],
                        "video_duration": link.get("video_duration"),
                        "created_by": user["username"],
                        "updated_by": user["username"],
                    }
                    links_to_create.append(link_data)

            # 物理删除不再需要的旧关联
            new_combinations = {
                (link["preset_point_id"], link["detection_type"])
                for link in preset_point_links
            }
            links_to_delete = [
                old_link
                for old_link in old_links
                if (old_link.preset_point_id, old_link.detection_type)
                not in new_combinations
            ]

            # 执行删除操作
            if links_to_delete:
                for link in links_to_delete:
                    await self.link_repo.delete_by_id(link.id)

            # 提交所有更改
            if links_to_create:
                await self.link_repo.create_batch(links_to_create)
            if links_to_update:
                await self.db.commit()

            total_links = len(links_to_create) + len(links_to_update)
            log_user_action(
                user["username"],
                "set_gimbal_inspection_project_preset_points",
                "success",
                f"设置云台巡检项目预设点关联成功，项目ID: {inspection_project_id}，关联数量: {total_links}",
            )

            # 重新获取项目信息（包含新关联）
            updated_project = await self.project_repo.get_by_id(inspection_project_id)

            total_links_count = len(links_to_create) + len(links_to_update)
            return ApiResponse.success(
                data=self._format_project_response(updated_project),
                message=f"设置预设点关联成功，共关联 {total_links_count} 个预设点",
            )

        except (ResourceNotFoundError, ValidationError, BusinessError) as e:
            logger.warning(f"设置云台巡检项目预设点关联失败: {e}")
            raise
        except Exception as e:
            logger.error(f"设置云台巡检项目预设点关联失败: {e}", exc_info=True)
            raise BusinessError(f"设置预设点关联失败: {str(e)}")

    async def delete_project_preset_point_link(
        self, link_id: str, user: dict
    ) -> Dict[str, Any]:
        """删除巡检项目的预设点关联

        Args:
            link_id: 关联ID
            user: 当前用户

        Returns:
            删除结果
        """
        try:
            link = await self.link_repo.get_by_id(link_id)
            if not link:
                raise ResourceNotFoundError(f"关联ID '{link_id}' 不存在")

            success = await self.link_repo.delete_by_id(link_id)

            if not success:
                raise BusinessError("删除预设点关联失败")

            log_user_action(
                user["username"],
                "delete_gimbal_inspection_project_preset_point_link",
                "success",
                f"删除云台巡检项目预设点关联成功，关联ID: {link_id}",
            )

            return ApiResponse.success(
                data={"link_id": link_id}, message="删除预设点关联成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"删除云台巡检项目预设点关联失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台巡检项目预设点关联失败: {e}", exc_info=True)
            raise BusinessError(f"删除预设点关联失败: {str(e)}")

