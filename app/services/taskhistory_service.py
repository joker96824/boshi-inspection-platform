"""
任务记录业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.taskhistory_repository import TaskHistoryRepository
from ..repositories.task_repository import TaskRepository
from ..repositories.itemhistory_repository import ItemHistoryRepository
from ..repositories.item_repository import ItemRepository
from ..repositories.point_repository import PointRepository
from ..repositories.taskresult_repository import TaskResultRepository
from ..schemas.taskhistory import TaskHistoryCreate, TaskHistoryUpdate, TaskHistoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, PermissionDeniedError, BusinessError
)
from ..core.task_status import TaskStatus
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class TaskHistoryService:
    """任务记录业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.taskhistory_repo = TaskHistoryRepository(db)
        self.task_repo = TaskRepository(db)
        self.itemhistory_repo = ItemHistoryRepository(db)
        self.item_repo = ItemRepository(db)
        self.point_repo = PointRepository(db)
        self.taskresult_repo = TaskResultRepository(db)
    
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
                data=await self._format_taskhistory_response(taskhistory),
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
                data=await self._format_taskhistory_response(taskhistory),
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
            
            items_data = []
            for th in taskhistories:
                items_data.append(await self._format_taskhistory_response(th))
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取任务记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取任务记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务记录列表失败")
    
    async def get_taskhistories(self, user: dict, page: Optional[int] = None, size: Optional[int] = None, 
                        task_id: str = None, record_status: str = None, record_batch: int = None,
                        start_time_from: str = None, start_time_to: str = None,
                        end_time_from: str = None, end_time_to: str = None) -> Dict[str, Any]:
        """获取任务记录列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if page is None or size is None:
                taskhistories, total = await self.taskhistory_repo.get_all(
                    None, None, task_id, record_status, record_batch,
                    start_time_from, start_time_to, end_time_from, end_time_to
                )
                items = []
                for taskhistory in taskhistories:
                    items.append(await self._format_taskhistory_response(taskhistory))
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取任务记录列表成功"
                )
            
            # 获取所有任务记录，无需基于用户ID过滤
            taskhistories, total = await self.taskhistory_repo.get_all(
                page, size, task_id, record_status, record_batch,
                start_time_from, start_time_to, end_time_from, end_time_to
            )
            
            # 格式化响应数据
            items = []
            for taskhistory in taskhistories:
                items.append(await self._format_taskhistory_response(taskhistory))
            
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
                data=await self._format_taskhistory_response(updated_taskhistory),
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
            
            return ApiResponse.success(
                data={"id": taskhistory_id},
                message="删除任务记录成功"
            )
            
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
    
    async def _format_taskhistory_response(self, taskhistory) -> Dict[str, Any]:
        """格式化任务记录响应数据"""
        # 格式化任务信息
        task_info = None
        if taskhistory.task:
            task = taskhistory.task
            # 获取任务的巡检点信息（通过task_items中的item获取对应的point）
            points_info = []
            if task.task_items:
                # 获取所有item的详细信息
                items = await self.item_repo.get_by_ids(task.task_items)
                
                # 收集所有唯一的point_id
                point_ids = set()
                item_point_map = {}  # item_id -> point_id
                for item in items:
                    if item and item.device and item.device.point:
                        point_id = item.device.point.id
                        point_ids.add(point_id)
                        item_point_map[item.id] = point_id
                
                # 获取所有point的详细信息
                if point_ids:
                    points = await self.point_repo.get_by_ids(list(point_ids))
                    
                    # 构建point_id -> point的映射
                    point_map = {p.id: p for p in points}
                    
                    # 构建points_info，去重并保持顺序
                    seen_points = set()
                    for item_id in task.task_items:
                        if item_id in item_point_map:
                            point_id = item_point_map[item_id]
                            if point_id not in seen_points and point_id in point_map:
                                point = point_map[point_id]
                                points_info.append({
                                    "id": point.id,
                                    "point_name": point.point_name,
                                    "x_coordinate": point.x_coordinate,
                                    "y_coordinate": point.y_coordinate,
                                    "enabled": point.enabled,
                                })
                                seen_points.add(point_id)
            
            task_info = {
                "id": task.id,
                "task_name": task.task_name,
                "robot_id": task.robot_id,
                "robot_name": task.robot.robot_name if task.robot else None,
                "task_items": task.task_items,
                "task_order": task.task_order,
                "task_res_prior": task.task_res_prior,
                "task_int_prior": task.task_int_prior,
                "total_duration": task.total_duration,
                "points": points_info,
            }
        
        # 格式化当前巡检点信息
        current_point_info = None
        if taskhistory.current_point:
            point = taskhistory.current_point
            current_point_info = {
                "id": point.id,
                "point_name": point.point_name,
                "x_coordinate": point.x_coordinate,
                "y_coordinate": point.y_coordinate,
                "enabled": point.enabled,
            }
        
        # 获取关联的巡检记录
        itemhistories = await self.itemhistory_repo.get_by_taskhistory_ids([taskhistory.id])
        itemhistories_info = []
        for itemhistory in itemhistories:
            item_info = None
            point_info = None
            detection_type_info = None
            
            if itemhistory.item:
                item = itemhistory.item
                # 巡检项目信息
                item_info = {
                    "id": item.id,
                    "item_name": item.item_name,
                    "item_info": item.item_info,
                    "device_id": item.device_id,
                    "robot_id": item.robot_id,
                    "detection_type_id": item.detection_type_id,
                    "enabled": item.enabled,
                }
                
                # 巡检点信息（通过 device 获取）
                if item.device and item.device.point:
                    point = item.device.point
                    point_info = {
                        "id": point.id,
                        "point_name": point.point_name,
                        "x_coordinate": point.x_coordinate,
                        "y_coordinate": point.y_coordinate,
                        "enabled": point.enabled,
                    }
                
                # 检测类型信息
                if item.detection_type:
                    detection_type = item.detection_type
                    detection_type_info = {
                        "id": detection_type.id,
                        "type_name": detection_type.type_name,
                        "type_code": detection_type.type_code,
                        "description": detection_type.description,
                    }
            
            itemhistories_info.append({
                "id": itemhistory.id,
                "item_id": itemhistory.item_id,
                "item_result": itemhistory.item_result,
                "process_status": itemhistory.process_status,
                "item": item_info,
                "point": point_info,
                "detection_type": detection_type_info,
                "created_at": itemhistory.created_at.strftime("%Y-%m-%dT%H:%M:%S") if itemhistory.created_at else None,
                "updated_at": itemhistory.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if itemhistory.updated_at else None,
            })
        
        # 获取任务结果（一对一关系）
        taskresult = await self.taskresult_repo.get_by_taskhistory_id(taskhistory.id)
        taskresult_info = None
        if taskresult:
            taskresult_info = {
                "id": taskresult.id,
                "taskhistory_id": taskresult.taskhistory_id,
                "record_batch": taskresult.record_batch,
                "result_status": taskresult.result_status,
                "process_status": taskresult.process_status,
                "result_point_id": taskresult.result_point_id,
                "result_item_id": taskresult.result_item_id,
                "result_file_url": taskresult.result_file_url,
                "result_collect_time": taskresult.result_collect_time.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.result_collect_time else None,
                "created_at": taskresult.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.created_at else None,
                "updated_at": taskresult.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskresult.updated_at else None,
            }
        
        return {
            "id": taskhistory.id,
            "task_id": taskhistory.task_id,
            "task": task_info,
            "record_start_time": taskhistory.record_start_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_start_time else None,
            "record_end_time": taskhistory.record_end_time.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.record_end_time else None,
            "record_status": taskhistory.record_status,
            "record_status_display": TaskStatus.get_status_display(taskhistory.record_status),
            "record_batch": taskhistory.record_batch,
            "current_point_id": taskhistory.current_point_id,
            "current_point": current_point_info,
            "current_item_id": taskhistory.current_item_id,
            "itemhistories": itemhistories_info,
            "taskresult": taskresult_info,
            "created_at": taskhistory.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.created_at else None,
            "updated_at": taskhistory.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskhistory.updated_at else None,
            "created_by": taskhistory.created_by,
            "updated_by": taskhistory.updated_by,
        }