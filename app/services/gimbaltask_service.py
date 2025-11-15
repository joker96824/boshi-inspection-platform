"""
云台任务业务逻辑服务
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..config.logging import get_logger, log_user_action
from ..core.exceptions import BusinessError, ResourceNotFoundError, ValidationError
from ..repositories.gimbal_repository import GimbalRepository
from ..repositories.gimbalinspectionproject_repository import (
    GimbalInspectionProjectRepository,
)
from ..repositories.gimbaltask_repository import GimbalTaskRepository
from ..schemas.gimbaltask import GimbalTaskCreate, GimbalTaskQuery, GimbalTaskUpdate
from ..utils.response import ApiResponse

logger = get_logger(__name__)


class GimbalTaskService:
    """云台任务业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_task_repo = GimbalTaskRepository(db)
        self.gimbal_repo = GimbalRepository(db)
        self.inspection_project_repo = GimbalInspectionProjectRepository(db)

    async def create_gimbal_task(
        self, task_data: GimbalTaskCreate, user: dict
    ) -> Dict[str, Any]:
        """创建云台任务"""
        try:
            if await self.gimbal_task_repo.exists_by_name(task_data.task_name):
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")

            gimbal = await self.gimbal_repo.get_by_id(task_data.gimbal_id)
            if not gimbal:
                raise ResourceNotFoundError(f"云台ID '{task_data.gimbal_id}' 不存在")

            create_data = task_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]

            task = await self.gimbal_task_repo.create(create_data)

            log_user_action(
                user["username"],
                "create_gimbal_task",
                "success",
                f"创建云台任务成功，ID: {task.id}",
            )

            return ApiResponse.success(
                data=self._format_gimbal_task_response(task),
                message="创建云台任务成功",
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台任务失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台任务失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台不存在，请检查云台ID是否正确")
            elif "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建云台任务失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")
            else:
                logger.error(f"创建云台任务失败-数据库完整性错误: {error_msg}")
                raise BusinessError("数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台任务失败: {str(e)}")

    async def get_gimbal_task_by_id(
        self, task_id: str, user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID获取云台任务"""
        try:
            task = await self.gimbal_task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")

            return ApiResponse.success(
                data=self._format_gimbal_task_response(task),
                message="获取云台任务成功",
            )

        except ResourceNotFoundError as e:
            logger.warning(f"获取云台任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务失败: {str(e)}")

    async def get_gimbal_tasks_by_ids(
        self, gimbaltask_ids: List[str], user: Optional[dict]
    ) -> Dict[str, Any]:
        """根据ID列表获取云台任务"""
        try:
            tasks = await self.gimbal_task_repo.get_by_ids(gimbaltask_ids)

            tasks_data = [self._format_gimbal_task_response(task) for task in tasks]

            return ApiResponse.success(
                data={"gimbal_tasks": tasks_data, "total": len(tasks_data)},
                message="获取云台任务列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台任务列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务列表失败: {str(e)}")

    async def get_gimbal_tasks(
        self, query: GimbalTaskQuery, user: Optional[dict]
    ) -> Dict[str, Any]:
        """获取云台任务列表"""
        try:
            tasks, total = await self.gimbal_task_repo.get_all(
                page=query.page,
                size=query.size,
                task_name=query.task_name,
                gimbal_id=query.gimbal_id,
                map_id=query.map_id,
            )

            tasks_data = [self._format_gimbal_task_response(task) for task in tasks]

            return ApiResponse.paginated(
                items=tasks_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台任务列表成功",
            )

        except Exception as e:
            logger.error(f"获取云台任务列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务列表失败: {str(e)}")

    async def update_gimbal_task(
        self, task_id: str, task_data: GimbalTaskUpdate, user: dict
    ) -> Dict[str, Any]:
        """更新云台任务"""
        try:
            existing_task = await self.gimbal_task_repo.get_by_id(task_id)
            if not existing_task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")

            if (
                task_data.task_name
                and task_data.task_name != existing_task.task_name
                and await self.gimbal_task_repo.exists_by_name(
                    task_data.task_name, task_id
                )
            ):
                raise BusinessError(f"云台任务名称 '{task_data.task_name}' 已存在")

            if task_data.gimbal_id and task_data.gimbal_id != existing_task.gimbal_id:
                gimbal = await self.gimbal_repo.get_by_id(task_data.gimbal_id)
                if not gimbal:
                    raise ResourceNotFoundError(f"云台ID '{task_data.gimbal_id}' 不存在")

            update_data = task_data.dict(exclude_unset=True)
            inspection_project_orders = update_data.pop("inspection_project_orders", None)
            sort_payload = None

            if inspection_project_orders:
                sort_payload = [
                    {
                        "inspection_project_id": item.inspection_project_id,
                        "sort_order": item.sort_order,
                    }
                    for item in inspection_project_orders
                ]

                project_ids = [item["inspection_project_id"] for item in sort_payload]
                if len(project_ids) != len(set(project_ids)):
                    raise ValidationError("巡检项目排序配置存在重复的巡检项目ID")

            update_data["updated_by"] = user["username"]

            updated_task = await self.gimbal_task_repo.update(task_id, update_data)

            if sort_payload:
                await self.inspection_project_repo.bulk_update_sort_orders(
                    task_id, sort_payload, user["username"]
                )
                updated_task = await self.gimbal_task_repo.get_by_id(task_id)

            log_user_action(
                user["username"],
                "update_gimbal_task",
                "success",
                f"更新云台任务成功，ID: {task_id}",
            )

            return ApiResponse.success(
                data=self._format_gimbal_task_response(updated_task),
                message="更新云台任务成功",
            )

        except (ResourceNotFoundError, BusinessError, ValidationError) as e:
            logger.warning(f"更新云台任务失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, "orig") else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"更新云台任务失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台不存在，请检查云台ID是否正确")
            else:
                logger.error(f"更新云台任务失败-数据库完整性错误: {error_msg}")
                raise BusinessError("数据完整性验证失败")
        except Exception as e:
            logger.error(f"更新云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台任务失败: {str(e)}")

    async def delete_gimbal_task(self, task_id: str, user: dict) -> Dict[str, Any]:
        """删除云台任务"""
        try:
            existing_task = await self.gimbal_task_repo.get_by_id(task_id)
            if not existing_task:
                raise ResourceNotFoundError(f"云台任务ID '{task_id}' 不存在")

            success = await self.gimbal_task_repo.soft_delete(task_id, user["username"])

            if not success:
                raise BusinessError("删除云台任务失败")

            log_user_action(
                user["username"],
                "delete_gimbal_task",
                "success",
                f"删除云台任务成功，ID: {task_id}",
            )

            return ApiResponse.success(
                data={"task_id": task_id}, message="删除云台任务成功"
            )

        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"删除云台任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台任务失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台任务失败: {str(e)}")

    async def get_gimbal_task_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台任务统计信息"""
        try:
            total_count = await self.gimbal_task_repo.count_all()

            stats = {"total_gimbal_tasks": total_count}

            return ApiResponse.success(
                data=stats, message="获取云台任务统计成功"
            )

        except Exception as e:
            logger.error(f"获取云台任务统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台任务统计失败: {str(e)}")

    def _format_gimbal_task_response(self, task) -> Dict[str, Any]:
        """格式化云台任务响应数据"""
        inspection_projects = sorted(
            [
                {
                    "id": project.id,
                    "task_name": project.task_name,
                    "detection_type": project.detection_type,
                    "sort_order": project.sort_order,
                    "x_coordinate": project.x_coordinate,
                    "y_coordinate": project.y_coordinate,
                    "fill_light": project.fill_light,
                }
                for project in getattr(task, "inspection_projects", []) or []
                if not project.is_deleted
            ],
            key=lambda item: item["sort_order"],
        )

        schedules = [
            {
                "id": schedule.id,
                "gimbaltask_id": schedule.gimbaltask_id,
                "schedule_name": schedule.schedule_name,
                "start_date": schedule.start_date.strftime("%Y-%m-%d")
                if schedule.start_date
                else None,
                "end_date": schedule.end_date.strftime("%Y-%m-%d")
                if schedule.end_date
                else None,
                "enabled": schedule.enabled,
                "cycle_type": schedule.cycle_type,
                "cycle_config": schedule.cycle_config,
                "time_mode": schedule.time_mode,
                "time_config": schedule.time_config,
                "frequency_display": schedule.frequency_display,
                "time_display_start": schedule.time_display_start.strftime("%H:%M")
                if schedule.time_display_start
                else None,
                "time_display_end": schedule.time_display_end.strftime("%H:%M")
                if schedule.time_display_end
                else None,
                "created_at": schedule.created_at.strftime("%Y-%m-%dT%H:%M:%S")
                if schedule.created_at
                else None,
                "updated_at": schedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                if schedule.updated_at
                else None,
            }
            for schedule in getattr(task, "schedules", []) or []
            if not schedule.is_deleted
        ]

        return {
            "id": task.id,
            "task_name": task.task_name,
            "gimbal_id": task.gimbal_id,
            "inspection_project_count": len(inspection_projects),
            "inspection_projects": inspection_projects,
            "schedule_count": len(schedules),
            "schedules": schedules,
            "created_at": task.created_at.strftime("%Y-%m-%dT%H:%M:%S")
            if task.created_at
            else None,
            "updated_at": task.updated_at.strftime("%Y-%m-%dT%H:%M:%S")
            if task.updated_at
            else None,
            "created_by": task.created_by,
            "updated_by": task.updated_by,
        }
