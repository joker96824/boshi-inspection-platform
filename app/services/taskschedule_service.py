"""
任务日程业务逻辑服务
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException

from ..core.exceptions import PermissionDeniedError, BusinessError, ResourceNotFoundError
from ..repositories.taskschedule_repository import TaskScheduleRepository
from ..repositories.task_repository import TaskRepository
from ..schemas.taskschedule import TaskScheduleCreate, TaskScheduleUpdate, TaskScheduleFrontendCreate
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
            create_data["enabled"] = create_data.get("enabled", True)
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            # 计算显示字段（如果未提供）
            if not create_data.get("frequency_display"):
                create_data["frequency_display"] = self._calculate_frequency_display(
                    create_data.get("cycle_type"),
                    create_data.get("cycle_config")
                )
            if not create_data.get("time_display_start") or not create_data.get("time_display_end"):
                time_start, time_end = self._calculate_time_display(create_data.get("time_config"))
                if not create_data.get("time_display_start"):
                    create_data["time_display_start"] = time_start
                if not create_data.get("time_display_end"):
                    create_data["time_display_end"] = time_end
            
            taskschedule = await self.taskschedule_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "创建任务日程",
                "成功",
                f"日程名称: {taskschedule.schedule_name}, 周期类型: {taskschedule.cycle_type}, 任务ID: {taskschedule.task_id}"
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
    
    async def create_taskschedule_from_frontend(self, frontend_data: TaskScheduleFrontendCreate, user: dict) -> Dict[str, Any]:
        """从前端格式数据创建任务日程"""
        try:
            # 将前端格式转换为后端格式
            backend_data = frontend_data.to_backend_format()
            
            # 创建 TaskScheduleCreate 对象
            taskschedule_data = TaskScheduleCreate(**backend_data)
            
            # 调用标准的创建方法
            return await self.create_taskschedule(taskschedule_data, user)
            
        except Exception as e:
            logger.error(f"从前端格式创建任务日程失败: {e}")
            raise
    
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
    
    async def get_taskschedules(self, user: dict, page: Optional[int] = None, size: Optional[int] = None, 
                                task_id: str = None, cycle_type: str = None, enabled: bool = None) -> Dict[str, Any]:
        """获取任务日程列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if page is None or size is None:
                taskschedules, total = await self.taskschedule_repo.get_all(
                    None, None, task_id, cycle_type, enabled
                )
                items = [self._format_taskschedule_response(ts) for ts in taskschedules]
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取任务日程列表成功"
                )
            
            # 获取所有任务日程，无需基于用户ID过滤
            taskschedules, total = await self.taskschedule_repo.get_all(
                page, size, task_id, cycle_type, enabled
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
            
            # 如果更新了周期或时间配置，重新计算显示字段
            if "cycle_type" in update_data or "cycle_config" in update_data:
                if "frequency_display" not in update_data:
                    cycle_type = update_data.get("cycle_type", taskschedule.cycle_type)
                    cycle_config = update_data.get("cycle_config", taskschedule.cycle_config)
                    update_data["frequency_display"] = self._calculate_frequency_display(cycle_type, cycle_config)
            
            if "time_config" in update_data:
                if "time_display_start" not in update_data or "time_display_end" not in update_data:
                    time_start, time_end = self._calculate_time_display(update_data.get("time_config"))
                    if "time_display_start" not in update_data:
                        update_data["time_display_start"] = time_start
                    if "time_display_end" not in update_data:
                        update_data["time_display_end"] = time_end
            
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
                f"日程ID: {taskschedule_id}, 名称: {taskschedule.schedule_name}"
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
    
    async def get_schedules_by_task_id(self, task_id: str, user: dict) -> Dict[str, Any]:
        """根据任务ID获取该任务的所有日程"""
        try:
            # 检查任务是否存在
            task = await self.task_repo.get_by_id(task_id)
            if not task:
                raise ResourceNotFoundError(f"任务ID '{task_id}' 不存在")
            
            # 获取所有日程（不分页）
            taskschedules = await self.taskschedule_repo.get_all_by_task_id(task_id)
            
            items = [self._format_taskschedule_response(ts) for ts in taskschedules]
            
            return ApiResponse.success(
                data={"items": items, "total": len(items), "task_id": task_id},
                message="获取任务日程列表成功"
            )
            
        except (ResourceNotFoundError, PermissionDeniedError) as e:
            logger.error(f"获取任务日程列表失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取任务日程列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取任务日程列表失败")
    
    def _format_taskschedule_response(self, taskschedule: TaskSchedule) -> Dict[str, Any]:
        """格式化任务日程响应数据"""
        # 获取任务名称（如果关联的任务已加载）
        task_name = None
        if taskschedule.task:
            task_name = taskschedule.task.task_name
        
        # 格式化时间显示字段（使用 %H:%M 格式，前端期望格式）
        time_display_start_str = taskschedule.time_display_start.strftime("%H:%M") if taskschedule.time_display_start else None
        time_display_end_str = taskschedule.time_display_end.strftime("%H:%M") if taskschedule.time_display_end else None
        
        return {
            "id": taskschedule.id,
            "task_id": taskschedule.task_id,
            "task_name": task_name,  # 新增：任务名称
            "schedule_name": taskschedule.schedule_name,
            "start_date": taskschedule.start_date.strftime("%Y-%m-%d") if taskschedule.start_date else None,
            "end_date": taskschedule.end_date.strftime("%Y-%m-%d") if taskschedule.end_date else None,
            "enabled": taskschedule.enabled,
            "item_count": taskschedule.item_count,
            "cycle_type": taskschedule.cycle_type,
            "cycle_config": taskschedule.cycle_config,
            "time_mode": taskschedule.time_mode,
            "time_config": taskschedule.time_config,
            "frequency_display": taskschedule.frequency_display,
            "time_display_start": time_display_start_str,
            "time_display_end": time_display_end_str,
            # 前端期望的字段名（映射）
            "frequency": taskschedule.frequency_display,  # 映射自 frequency_display
            "cycle": taskschedule.frequency_display,  # 改为映射自 frequency_display（与 frequency 保持一致）
            "startTime": time_display_start_str,  # 映射自 time_display_start（camelCase）
            "endTime": time_display_end_str,  # 映射自 time_display_end（camelCase）
            "start_time": time_display_start_str,  # 映射自 time_display_start（snake_case）
            "end_time": time_display_end_str,  # 映射自 time_display_end（snake_case）
            "created_at": taskschedule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if taskschedule.created_at else None,
            "updated_at": taskschedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if taskschedule.updated_at else None,
            "created_by": taskschedule.created_by,
            "updated_by": taskschedule.updated_by,
            "is_deleted": taskschedule.is_deleted,
        }
    
    def _calculate_frequency_display(self, cycle_type: Optional[str], cycle_config: Optional[Dict[str, Any]]) -> Optional[str]:
        """计算周期显示文本"""
        if not cycle_type:
            return None
        
        if cycle_type == 'daily':
            return '每天'
        elif cycle_type == 'monthly_days' and cycle_config and 'selectedDays' in cycle_config:
            days = cycle_config['selectedDays']
            if days:
                days_str = '、'.join([str(d) for d in sorted(days)])
                return f'每月{days_str}日'
        elif cycle_type == 'weekly' and cycle_config and 'selectedWeeks' in cycle_config:
            week_names = ['一', '二', '三', '四', '五', '六', '日']
            weeks = [week_names[w-1] for w in sorted(cycle_config['selectedWeeks']) if 1 <= w <= 7]
            if weeks:
                weeks_str = '、'.join([f'周{w}' for w in weeks])
                return f'每{weeks_str}'
        elif cycle_type == 'interval' and cycle_config and 'intervalDays' in cycle_config:
            days = cycle_config['intervalDays']
            return f'每{days}天'
        
        return None
    
    def _calculate_time_display(self, time_config: Optional[Dict[str, Any]]) -> Tuple[Optional[time], Optional[time]]:
        """计算时间显示字段"""
        
        if not time_config:
            return None, None
        
        if 'customTimes' in time_config and time_config['customTimes']:
            times = time_config['customTimes']
            if times:
                first_time_str = times[0]
                last_time_str = times[-1]
                try:
                    # 处理 HH:MM 格式
                    if len(first_time_str) == 5:  # HH:MM
                        first_time = time.fromisoformat(first_time_str + ':00')
                    else:  # HH:MM:SS
                        first_time = time.fromisoformat(first_time_str)
                    
                    if len(last_time_str) == 5:  # HH:MM
                        last_time = time.fromisoformat(last_time_str + ':00')
                    else:  # HH:MM:SS
                        last_time = time.fromisoformat(last_time_str)
                    
                    return first_time, last_time
                except Exception as e:
                    logger.warning(f"解析时间失败: {e}, time_str: {first_time_str}/{last_time_str}")
                    return None, None
        
        if 'intervalTimeRange' in time_config and time_config['intervalTimeRange']:
            time_range = time_config['intervalTimeRange']
            if len(time_range) >= 2:
                try:
                    start_str = time_range[0]
                    end_str = time_range[1]
                    
                    if len(start_str) == 5:  # HH:MM
                        start_time = time.fromisoformat(start_str + ':00')
                    else:  # HH:MM:SS
                        start_time = time.fromisoformat(start_str)
                    
                    if len(end_str) == 5:  # HH:MM
                        end_time = time.fromisoformat(end_str + ':00')
                    else:  # HH:MM:SS
                        end_time = time.fromisoformat(end_str)
                    
                    return start_time, end_time
                except Exception as e:
                    logger.warning(f"解析时间范围失败: {e}, time_range: {time_range}")
                    return None, None
        
        return None, None
