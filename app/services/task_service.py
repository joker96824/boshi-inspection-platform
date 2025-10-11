"""
任务业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.task_repository import TaskRepository
from ..repositories.map_repository import MapRepository
from ..repositories.robot_repository import RobotRepository
from ..repositories.item_repository import ItemRepository
from ..schemas.task import TaskCreate, TaskUpdate, TaskQuery
from ..core.exceptions import (
    ResourceNotFoundError, PermissionDeniedError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class TaskService:
    """任务业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.task_repo = TaskRepository(db)
        self.map_repo = MapRepository(db)
        self.robot_repo = RobotRepository(db)
        self.item_repo = ItemRepository(db)
    
    async def create_task(self, task_data: TaskCreate, user: dict) -> Dict[str, Any]:
        """创建任务"""
        try:
            # 检查地图是否存在
            map_obj = await self.map_repo.get_by_id(task_data.map_id)
            if not map_obj:
                raise ResourceNotFoundError(f"地图ID '{task_data.map_id}' 不存在")
            
            # 检查机器人是否存在
            robot = await self.robot_repo.get_by_id(task_data.robot_id)
            if not robot:
                raise ResourceNotFoundError(f"机器人ID '{task_data.robot_id}' 不存在")
            
            # 验证task_items中的所有item_id是否存在
            if task_data.task_items:
                await self._validate_task_items(task_data.task_items)
            
            # 地图存在性检查已完成，无需额外权限检查
            
            create_data = task_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            task = await self.task_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_task",
                "success",
                f"创建任务成功，ID: {task.id}"
            )
            
            return ApiResponse.success(
                data=self._format_task_response(task),
                message="创建任务成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            logger.warning(f"创建任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise HTTPException(status_code=500, detail="创建任务失败")
    
    async def get_task_by_id(self, task_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取任务"""
        try:
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            # 任务存在性检查已完成，无需额外权限检查
            
            return ApiResponse.success(
                data=self._format_task_response(task),
                message="获取任务成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务失败")
    
    async def get_tasks_by_ids(self, task_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取任务"""
        try:
            tasks = await self.task_repo.get_by_ids(task_ids)
            
            items_data = [self._format_task_response(task) for task in tasks]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务列表失败")
    
    async def get_tasks(self, user: dict, page: int = 1, size: int = 20, 
                        task_name: str = None, map_id: str = None, robot_id: str = None,
                        sort_by: str = "task_order", sort_order: str = "asc") -> Dict[str, Any]:
        """获取任务列表"""
        try:
            # 获取所有任务，无需基于用户ID过滤
            tasks, total = await self.task_repo.get_all(
                page, size, task_name, map_id, robot_id, sort_by, sort_order
            )
            
            # 格式化响应数据
            items = [self._format_task_response(task) for task in tasks]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取任务列表成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务列表失败")
    
    async def update_task(self, task_id: str, task_data: TaskUpdate, user: dict) -> Dict[str, Any]:
        """更新任务"""
        try:
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            # 验证task_items中的所有item_id是否存在
            if task_data.task_items is not None:
                await self._validate_task_items(task_data.task_items)
            
            # 任务存在性检查已完成，无需额外权限检查
            
            update_data = task_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_task = await self.task_repo.update(task_id, update_data)
            
            log_user_action(
                user["username"],
                "update_task",
                "success",
                f"更新任务成功，ID: {task_id}"
            )
            
            return ApiResponse.success(
                data=self._format_task_response(updated_task),
                message="更新任务成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"更新任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新任务失败: {e}")
            raise HTTPException(status_code=500, detail="更新任务失败")
    
    async def delete_task(self, task_id: str, user: dict) -> Dict[str, Any]:
        """删除任务"""
        try:
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            # 任务存在性检查已完成，无需额外权限检查
            
            await self.task_repo.soft_delete(task_id)
            
            log_user_action(
                user["username"],
                "delete_task",
                "success",
                f"删除任务成功，ID: {task_id}"
            )
            
            return ApiResponse.success(message="删除任务成功")
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"删除任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除任务失败: {e}")
            raise HTTPException(status_code=500, detail="删除任务失败")
    
    async def _validate_task_items(self, task_items: List[str]) -> None:
        """验证task_items中的所有item_id是否存在
        
        Args:
            task_items: 巡检项目ID列表
            
        Raises:
            ResourceNotFoundError: 当某个item_id不存在时
        """
        if not task_items:
            return
        
        # 逐个验证每个item_id是否存在
        for item_id in task_items:
            item = await self.item_repo.get_by_id(item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
    
    def _format_task_response(self, task) -> Dict[str, Any]:
        """格式化任务响应数据"""
        return {
            "id": task.id,
            "task_name": task.task_name,
            "map_id": task.map_id,
            "robot_id": task.robot_id,
            "task_items": task.task_items,
            "task_order": task.task_order,
            "task_res_prior": task.task_res_prior,
            "task_int_prior": task.task_int_prior,
            "created_at": task.created_at.strftime("%Y-%m-%dT%H:%M:%S") if task.created_at else None,
            "updated_at": task.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if task.updated_at else None,
            "created_by": task.created_by,
            "updated_by": task.updated_by,
        }
