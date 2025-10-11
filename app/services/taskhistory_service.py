"""
任务记录业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.taskhistory_repository import TaskHistoryRepository
from ..repositories.task_repository import TaskRepository
from ..schemas.taskhistory import TaskHistoryCreate, TaskHistoryUpdate, TaskHistoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, PermissionDeniedError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class TaskHistoryService:
    """任务记录业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.taskhistory_repo = TaskHistoryRepository(db)
        self.task_repo = TaskRepository(db)
    
    async def create_taskhistory(self, taskhistory_data: TaskHistoryCreate, user: dict) -> Dict[str, Any]:
        """创建任务记录"""
        try:
            # 检查任务是否存在
            task = await self.task_repo.get_by_id(taskhistory_data.task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{taskhistory_data.task_id}' 不存在")
            
            # 任务存在性检查已完成，无需额外权限检查
            
            create_data = taskhistory_data.dict()
            # 转换字符串时间为 datetime 对象
            from datetime import datetime
            create_data["record_start_time"] = datetime.strptime(create_data["record_start_time"], "%Y-%m-%dT%H:%M:%S")
            if create_data.get("record_end_time"):
                create_data["record_end_time"] = datetime.strptime(create_data["record_end_time"], "%Y-%m-%dT%H:%M:%S")
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            taskhistory = await self.taskhistory_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_taskhistory",
                "success",
                f"创建任务记录成功，ID: {taskhistory.id}"
            )
            
            return ApiResponse.success(
                data=self._format_taskhistory_response(taskhistory),
                message="创建任务记录成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            logger.warning(f"创建任务记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建任务记录失败: {e}")
            raise HTTPException(status_code=500, detail="创建任务记录失败")
    
    async def get_taskhistory_by_id(self, taskhistory_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取任务记录"""
        try:
            taskhistory = await self.taskhistory_repo.get_by_id(taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
            
            # 任务记录存在性检查已完成，无需额外权限检查
            
            return ApiResponse.success(
                data=self._format_taskhistory_response(taskhistory),
                message="获取任务记录成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务记录失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务记录失败")
    
    async def get_taskhistories_by_ids(self, taskhistory_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取任务记录"""
        try:
            taskhistories = await self.taskhistory_repo.get_by_ids(taskhistory_ids)
            
            items_data = [self._format_taskhistory_response(th) for th in taskhistories]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务记录列表失败")
    
    async def get_taskhistories(self, user: dict, page: int = 1, size: int = 20, 
                        task_id: str = None, record_status: str = None, record_batch: int = None,
                        start_time_from: str = None, start_time_to: str = None,
                        end_time_from: str = None, end_time_to: str = None) -> Dict[str, Any]:
        """获取任务记录列表"""
        try:
            # 获取所有任务记录，无需基于用户ID过滤
            taskhistories, total = await self.taskhistory_repo.get_all(
                page, size, task_id, record_status, record_batch,
                start_time_from, start_time_to, end_time_from, end_time_to
            )
            
            # 格式化响应数据
            items = [self._format_taskhistory_response(taskhistory) for taskhistory in taskhistories]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取任务记录列表成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务记录列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务记录列表失败")
    
    async def update_taskhistory(self, taskhistory_id: str, taskhistory_data: TaskHistoryUpdate, user: dict) -> Dict[str, Any]:
        """更新任务记录"""
        try:
            taskhistory = await self.taskhistory_repo.get_by_id(taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
            
            # 任务记录存在性检查已完成，无需额外权限检查
            
            update_data = taskhistory_data.dict(exclude_unset=True)
            # 转换字符串时间为 datetime 对象
            from datetime import datetime
            if "record_start_time" in update_data:
                update_data["record_start_time"] = datetime.strptime(update_data["record_start_time"], "%Y-%m-%dT%H:%M:%S")
            if "record_end_time" in update_data and update_data["record_end_time"]:
                update_data["record_end_time"] = datetime.strptime(update_data["record_end_time"], "%Y-%m-%dT%H:%M:%S")
            update_data["updated_by"] = user["username"]
            
            updated_taskhistory = await self.taskhistory_repo.update(taskhistory_id, update_data)
            
            log_user_action(
                user["username"],
                "update_taskhistory",
                "success",
                f"更新任务记录成功，ID: {taskhistory_id}"
            )
            
            return ApiResponse.success(
                data=self._format_taskhistory_response(updated_taskhistory),
                message="更新任务记录成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"更新任务记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新任务记录失败: {e}")
            raise HTTPException(status_code=500, detail="更新任务记录失败")
    
    async def delete_taskhistory(self, taskhistory_id: str, user: dict) -> Dict[str, Any]:
        """删除任务记录"""
        try:
            taskhistory = await self.taskhistory_repo.get_by_id(taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
            
            # 任务记录存在性检查已完成，无需额外权限检查
            
            await self.taskhistory_repo.soft_delete(taskhistory_id)
            
            log_user_action(
                user["username"],
                "delete_taskhistory",
                "success",
                f"删除任务记录成功，ID: {taskhistory_id}"
            )
            
            return ApiResponse.success(message="删除任务记录成功")
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"删除任务记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除任务记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除任务记录失败")
    
    async def get_taskhistory_stats(self, user: dict) -> Dict[str, Any]:
        """获取任务记录统计信息"""
        try:
            # 这里可以根据需要实现统计逻辑
            # 例如：按状态统计、按时间统计等
            return ApiResponse.success(
                data={"message": "统计功能待实现"},
                message="获取统计信息成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务记录统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取统计信息失败")
    
    def _format_taskhistory_response(self, taskhistory) -> Dict[str, Any]:
        """格式化任务记录响应数据"""
        return {
            "id": taskhistory.id,
            "task_id": taskhistory.task_id,
            "record_start_time": taskhistory.record_start_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_start_time else None,
            "record_end_time": taskhistory.record_end_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_end_time else None,
            "record_status": taskhistory.record_status,
            "record_batch": taskhistory.record_batch,
            "created_at": taskhistory.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.created_at else None,
            "updated_at": taskhistory.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.updated_at else None,
            "created_by": taskhistory.created_by,
            "updated_by": taskhistory.updated_by,
        }