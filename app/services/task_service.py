"""
任务业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.task_repository import TaskRepository
from ..repositories.map_repository import MapRepository
from ..repositories.robot_repository import RobotRepository
from ..repositories.item_repository import ItemRepository
from ..schemas.task import TaskCreate, TaskUpdate, TaskQuery
from ..models.taskschedule import TaskSchedule
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
            # 检查机器人是否存在
            robot = await self.robot_repo.get_by_id(task_data.robot_id)
            if not robot:
                raise ResourceNotFoundError(f"机器人ID '{task_data.robot_id}' 不存在")
            
            # 验证task_items中的所有item_id是否存在
            if task_data.task_items:
                await self._validate_task_items(task_data.task_items)
            
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
                data=await self._format_task_response(task),
                message="创建任务成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError, BusinessError) as e:
            logger.warning(f"创建任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建任务失败: {e}")
            raise HTTPException(status_code=500, detail="创建任务失败")
    
    async def get_task_by_id(self, task_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取任务"""
        try:
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            # 任务存在性检查已完成，无需额外权限检查
            
            return ApiResponse.success(
                data=await self._format_task_response(task),
                message="获取任务成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.warning(f"获取任务失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务失败")
    
    async def get_tasks_by_ids(self, task_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取任务"""
        try:
            tasks = await self.task_repo.get_by_ids(task_ids)
            
            items_data = []
            for task in tasks:
                items_data.append(await self._format_task_response(task))
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务列表失败")
    
    async def get_tasks(self, user: Optional[dict], page: Optional[int] = None, size: Optional[int] = None, 
                        task_name: str = None, robot_id: str = None,
                        sort_by: str = "task_order", sort_order: str = "asc") -> Dict[str, Any]:
        """获取任务列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if page is None or size is None:
                tasks, total = await self.task_repo.get_all(
                    None, None, task_name, robot_id, sort_by, sort_order
                )
                items = []
                for task in tasks:
                    items.append(await self._format_task_response(task))
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取任务列表成功"
                )
            
            # 获取所有任务，无需基于用户ID过滤
            tasks, total = await self.task_repo.get_all(
                page, size, task_name, robot_id, sort_by, sort_order
            )
            
            # 格式化响应数据
            items = []
            for task in tasks:
                items.append(await self._format_task_response(task))
            
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
                data=await self._format_task_response(updated_task),
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
            
            return ApiResponse.success(
                data={"id": task_id},
                message="删除任务成功"
            )
            
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
    
    async def _format_task_response(self, task) -> Dict[str, Any]:
        """格式化任务响应数据"""
        # 加载 task_items 的完整信息
        task_items_info = []
        if task.task_items and isinstance(task.task_items, list) and len(task.task_items) > 0:
            items = await self.item_repo.get_by_ids(task.task_items)
            # 保持原始顺序，按照 task.task_items 的顺序排列
            item_dict = {item.id: item for item in items}
            for item_id in task.task_items:
                if item_id in item_dict:
                    item = item_dict[item_id]
                    task_items_info.append({
                        "id": item.id,
                        "item_name": item.item_name,
                        "item_info": item.item_info,
                        "point_id": item.point_id,
                        "point_name": item.point.point_name if item.point else None,
                        "created_at": item.created_at.strftime("%Y-%m-%dT%H:%M:%S") if item.created_at else None,
                        "updated_at": item.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if item.updated_at else None,
                        "created_by": item.created_by,
                        "updated_by": item.updated_by,
                    })
        
        # 格式化 schedules 列表
        schedules_info = []
        if task.schedules:
            # 只包含未删除的日程
            active_schedules = [s for s in task.schedules if not s.is_deleted]
            for schedule in active_schedules:
                schedules_info.append(self._format_schedule_response(schedule))
        
        return {
            "id": task.id,
            "task_name": task.task_name,
            "robot_id": task.robot_id,
            "robot_name": task.robot.robot_name if task.robot else None,
            "task_items": task_items_info,  # 完整的 item 信息列表
            "schedules": schedules_info,  # 日程列表
            "task_order": task.task_order,
            "task_res_prior": task.task_res_prior,
            "task_int_prior": task.task_int_prior,
            "created_at": task.created_at.strftime("%Y-%m-%dT%H:%M:%S") if task.created_at else None,
            "updated_at": task.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if task.updated_at else None,
            "created_by": task.created_by,
            "updated_by": task.updated_by,
        }
    
    def _format_schedule_response(self, schedule: TaskSchedule) -> Dict[str, Any]:
        """格式化任务日程响应数据（用于 task 响应中）"""
        # 格式化时间显示字段（使用 %H:%M 格式，前端期望格式）
        time_display_start_str = schedule.time_display_start.strftime("%H:%M") if schedule.time_display_start else None
        time_display_end_str = schedule.time_display_end.strftime("%H:%M") if schedule.time_display_end else None
        
        return {
            "id": schedule.id,
            "task_id": schedule.task_id,
            "schedule_name": schedule.schedule_name,
            "start_date": schedule.start_date.strftime("%Y-%m-%d") if schedule.start_date else None,
            "end_date": schedule.end_date.strftime("%Y-%m-%d") if schedule.end_date else None,
            "enabled": schedule.enabled,
            "item_count": schedule.item_count,
            "cycle_type": schedule.cycle_type,
            "cycle_config": schedule.cycle_config,
            "time_mode": schedule.time_mode,
            "time_config": schedule.time_config,
            "frequency_display": schedule.frequency_display,
            "time_display_start": time_display_start_str,
            "time_display_end": time_display_end_str,
            "frequency": schedule.frequency_display,
            "cycle": schedule.frequency_display,
            "startTime": time_display_start_str,
            "endTime": time_display_end_str,
            "start_time": time_display_start_str,
            "end_time": time_display_end_str,
            "created_at": schedule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.created_at else None,
            "updated_at": schedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.updated_at else None,
            "created_by": schedule.created_by,
            "updated_by": schedule.updated_by,
        }
