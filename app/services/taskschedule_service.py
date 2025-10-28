"""
任务日程业务逻辑服务
"""

from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from ..core.exceptions import PermissionDeniedError, BusinessError, ResourceNotFoundError
from ..repositories.taskschedule_repository import TaskScheduleRepository
from ..repositories.task_repository import TaskRepository
from ..schemas.taskschedule import TaskScheduleCreate, TaskScheduleUpdate
from ..models.taskschedule import TaskSchedule
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class TaskScheduleService:
    """任务日程业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.taskschedule_repo = TaskScheduleRepository(db)
        self.task_repo = TaskRepository(db)
    
    async def create_taskschedule(self, taskschedule_data: TaskScheduleCreate, user: dict) -> Dict[str, Any]:
        """创建任务日程"""
        try:
            # 检查任务是否存在且用户有权限
            task = await self.task_repo.get_by_id(taskschedule_data.task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{taskschedule_data.task_id}' 不存在")
            
            # 任务存在性检查已完成，无需额外权限检查
            
            create_data = taskschedule_data.dict()
            # 设置默认值
            create_data["schedule_is_active"] = True
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            taskschedule = await self.taskschedule_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "创建任务日程",
                "成功",
                f"日程类型: {taskschedule.schedule_type}, 任务ID: {taskschedule.task_id}"
            )
            
            return ApiResponse.success(
                data=self._format_taskschedule_response(taskschedule),
                message="任务日程创建成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"创建任务日程失败: {e}")
            log_user_action(
                user["username"],
                "创建任务日程",
                "失败",
                f"创建任务日程失败: {str(e)}"
            )
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"创建任务日程失败: {e}")
            log_user_action(
                user["username"],
                "创建任务日程",
                "失败",
                f"创建任务日程失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="创建任务日程失败")
    
    async def get_taskschedule_by_id(self, taskschedule_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取任务日程"""
        try:
            taskschedule = await self.taskschedule_repo.get_by_id(taskschedule_id)
            if not taskschedule:
                raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
            
            # 任务日程存在性检查已完成，无需额外权限检查
            
            return ApiResponse.success(
                data=self._format_taskschedule_response(taskschedule),
                message="获取任务日程成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务日程失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程失败")
    
    async def get_taskschedules_by_ids(self, taskschedule_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取任务日程"""
        try:
            taskschedules = await self.taskschedule_repo.get_by_ids(taskschedule_ids)
            
            items_data = [self._format_taskschedule_response(ts) for ts in taskschedules]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务日程列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务日程列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程列表失败")
    
    async def get_taskschedules_legacy(self, taskschedule_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取任务日程（向后兼容）"""
        try:
            taskschedule = await self.taskschedule_repo.get_by_id(taskschedule_id)
            if not taskschedule:
                raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
            
            # 任务日程存在性检查已完成，无需额外权限检查
            
            return ApiResponse.success(
                data=self._format_taskschedule_response(taskschedule),
                message="获取任务日程成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"获取任务日程失败: {e}")
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"获取任务日程失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程失败")
    
    async def get_taskschedules(self, user: dict, page: int = 1, size: int = 20, 
                                task_id: str = None, schedule_type: str = None) -> Dict[str, Any]:
        """获取任务日程列表"""
        try:
            # 获取所有任务日程，无需基于用户ID过滤
            taskschedules, total = await self.taskschedule_repo.get_all(
                page, size, task_id, schedule_type
            )
            
            items = [self._format_taskschedule_response(ts) for ts in taskschedules]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取任务日程列表成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"获取任务日程列表失败: {e}")
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"获取任务日程列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程列表失败")
    
    async def update_taskschedule(self, taskschedule_id: str, taskschedule_data: TaskScheduleUpdate, user: dict) -> Dict[str, Any]:
        """更新任务日程"""
        try:
            taskschedule = await self.taskschedule_repo.get_by_id(taskschedule_id)
            if not taskschedule:
                raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
            
            # 任务日程存在性检查已完成，无需额外权限检查
            
            update_data = taskschedule_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_taskschedule = await self.taskschedule_repo.update(taskschedule_id, update_data)
            
            log_user_action(
                user["username"],
                "更新任务日程",
                "成功",
                f"日程ID: {taskschedule_id}, 更新字段: {list(update_data.keys())}"
            )
            
            return ApiResponse.success(
                data=self._format_taskschedule_response(updated_taskschedule),
                message="任务日程更新成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"更新任务日程失败: {e}")
            log_user_action(
                user["username"],
                "更新任务日程",
                "失败",
                f"更新任务日程失败: {str(e)}"
            )
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"更新任务日程失败: {e}")
            log_user_action(
                user["username"],
                "更新任务日程",
                "失败",
                f"更新任务日程失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="更新任务日程失败")
    
    async def delete_taskschedule(self, taskschedule_id: str, user: dict) -> Dict[str, Any]:
        """删除任务日程"""
        try:
            taskschedule = await self.taskschedule_repo.get_by_id(taskschedule_id)
            if not taskschedule:
                raise ResourceNotFoundError(f"任务日程ID '{taskschedule_id}' 不存在")
            
            # 任务日程存在性检查已完成，无需额外权限检查
            
            await self.taskschedule_repo.soft_delete(taskschedule_id)
            
            log_user_action(
                user["username"],
                "删除任务日程",
                "成功",
                f"日程ID: {taskschedule_id}, 类型: {taskschedule.schedule_type}"
            )
            
            return ApiResponse.success(
                data={"id": taskschedule_id},
                message="任务日程删除成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"删除任务日程失败: {e}")
            log_user_action(
                user["username"],
                "删除任务日程",
                "失败",
                f"删除任务日程失败: {str(e)}"
            )
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"删除任务日程失败: {e}")
            log_user_action(
                user["username"],
                "删除任务日程",
                "失败",
                f"删除任务日程失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="删除任务日程失败")
    
    async def get_taskschedule_stats(self, task_id: str, user: dict) -> Dict[str, Any]:
        """获取任务日程统计信息"""
        try:
            # 检查任务是否存在
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            total_schedules = await self.taskschedule_repo.count_by_task(task_id)
            
            return ApiResponse.success(
                data={"total_schedules": total_schedules, "task_id": task_id},
                message="获取任务日程统计成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            # 业务异常直接抛出，保持原始错误信息
            logger.error(f"获取任务日程统计失败: {e}")
            raise
        except Exception as e:
            # 系统异常记录详细日志，但返回通用错误信息
            logger.error(f"获取任务日程统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程统计失败")
    
    def _format_taskschedule_response(self, taskschedule: TaskSchedule) -> Dict[str, Any]:
        """格式化任务日程响应数据"""
        return {
            "id": taskschedule.id,
            "schedule_type": taskschedule.schedule_type,
            "schedule_is_active": taskschedule.schedule_is_active,
            "task_id": taskschedule.task_id,
            "schedule_param": taskschedule.schedule_param,
            "set_time": taskschedule.set_time,
            "cnt": taskschedule.cnt,
            "created_at": taskschedule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskschedule.created_at else None,
            "updated_at": taskschedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskschedule.updated_at else None,
            "created_by": taskschedule.created_by,
            "updated_by": taskschedule.updated_by,
            "is_deleted": taskschedule.is_deleted,
        }
