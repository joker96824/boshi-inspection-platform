"""
云台日程业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.gimbalschedule_repository import GimbalScheduleRepository
from ..repositories.gimbaltask_repository import GimbalTaskRepository
from ..schemas.gimbalschedule import GimbalScheduleCreate, GimbalScheduleUpdate, GimbalScheduleQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalScheduleService:
    """云台日程业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_schedule_repo = GimbalScheduleRepository(db)
        self.gimbal_task_repo = GimbalTaskRepository(db)
    
    async def create_gimbal_schedule(self, schedule_data: GimbalScheduleCreate, user: dict) -> Dict[str, Any]:
        """创建云台日程"""
        try:
            # 检查云台任务是否存在
            gimbal_task = await self.gimbal_task_repo.get_by_id(schedule_data.gimbaltask_id)
            if not gimbal_task:
                raise ResourceNotFoundError(f"云台任务ID '{schedule_data.gimbaltask_id}' 不存在")
            
            create_data = schedule_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            schedule = await self.gimbal_schedule_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_gimbal_schedule",
                "success",
                f"创建云台日程成功，ID: {schedule.id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_schedule_response(schedule),
                message="创建云台日程成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台日程失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台日程失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台任务不存在，请检查云台任务ID是否正确")
            elif "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建云台日程失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"云台日程名称 '{schedule_data.schedule_name}' 已存在")
            else:
                logger.error(f"创建云台日程失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台日程失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台日程失败: {str(e)}")
    
    async def get_gimbal_schedule_by_id(self, schedule_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取云台日程"""
        try:
            schedule = await self.gimbal_schedule_repo.get_by_id(schedule_id)
            if not schedule:
                raise ResourceNotFoundError(f"云台日程ID '{schedule_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_gimbal_schedule_response(schedule),
                message="获取云台日程成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取云台日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台日程失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台日程失败: {str(e)}")
    
    async def get_gimbal_schedules_by_ids(self, gimbalschedule_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取云台日程"""
        try:
            schedules = await self.gimbal_schedule_repo.get_by_ids(gimbalschedule_ids)
            
            schedules_data = [self._format_gimbal_schedule_response(schedule) for schedule in schedules]
            
            return ApiResponse.success(
                data={"gimbal_schedules": schedules_data, "total": len(schedules_data)},
                message="获取云台日程列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台日程列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台日程列表失败: {str(e)}")
    
    async def get_gimbal_schedules(self, query: GimbalScheduleQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台日程列表"""
        try:
            schedules, total = await self.gimbal_schedule_repo.get_all(
                page=query.page,
                size=query.size,
                schedule_type=query.schedule_type,
                schedule_is_active=query.schedule_is_active,
                gimbaltask_id=query.gimbaltask_id
            )
            
            # 格式化响应数据
            schedules_data = [self._format_gimbal_schedule_response(schedule) for schedule in schedules]
            
            return ApiResponse.paginated(
                items=schedules_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台日程列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台日程列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台日程列表失败: {str(e)}")
    
    async def update_gimbal_schedule(self, schedule_id: str, schedule_data: GimbalScheduleUpdate, user: dict) -> Dict[str, Any]:
        """更新云台日程"""
        try:
            # 检查云台日程是否存在
            existing_schedule = await self.gimbal_schedule_repo.get_by_id(schedule_id)
            if not existing_schedule:
                raise ResourceNotFoundError(f"云台日程ID '{schedule_id}' 不存在")
            
            # 如果更新了云台任务ID，检查云台任务是否存在
            if schedule_data.gimbaltask_id and schedule_data.gimbaltask_id != existing_schedule.gimbaltask_id:
                gimbal_task = await self.gimbal_task_repo.get_by_id(schedule_data.gimbaltask_id)
                if not gimbal_task:
                    raise ResourceNotFoundError(f"云台任务ID '{schedule_data.gimbaltask_id}' 不存在")
            
            update_data = schedule_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_schedule = await self.gimbal_schedule_repo.update(schedule_id, update_data)
            
            log_user_action(
                user["username"],
                "update_gimbal_schedule",
                "success",
                f"更新云台日程成功，ID: {schedule_id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_schedule_response(updated_schedule),
                message="更新云台日程成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台日程失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台日程失败: {str(e)}")
    
    async def delete_gimbal_schedule(self, schedule_id: str, user: dict) -> Dict[str, Any]:
        """删除云台日程"""
        try:
            # 检查云台日程是否存在
            existing_schedule = await self.gimbal_schedule_repo.get_by_id(schedule_id)
            if not existing_schedule:
                raise ResourceNotFoundError(f"云台日程ID '{schedule_id}' 不存在")
            
            # 删除云台日程
            success = await self.gimbal_schedule_repo.soft_delete(schedule_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal_schedule",
                    "success",
                    f"删除云台日程成功，ID: {schedule_id}"
                )
                
                return ApiResponse.success(
                    data={"schedule_id": schedule_id},
                    message="删除云台日程成功"
                )
            else:
                raise BusinessError("删除云台日程失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除云台日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台日程失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台日程失败: {str(e)}")
    
    async def get_gimbal_schedule_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台日程统计信息"""
        try:
            total_count = await self.gimbal_schedule_repo.count_all()
            active_count = await self.gimbal_schedule_repo.count_active()
            
            stats = {
                "total_schedules": total_count,
                "active_schedules": active_count,
                "inactive_schedules": total_count - active_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取云台日程统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台日程统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台日程统计失败: {str(e)}")
    
    def _format_gimbal_schedule_response(self, schedule) -> Dict[str, Any]:
        """格式化云台日程响应数据"""
        return {
            "id": schedule.id,
            "schedule_type": schedule.schedule_type,
            "schedule_is_active": schedule.schedule_is_active,
            "gimbaltask_id": schedule.gimbaltask_id,
            "schedule_param": schedule.schedule_param,
            "set_time": schedule.set_time,
            "created_at": schedule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.created_at else None,
            "updated_at": schedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.updated_at else None,
            "created_by": schedule.created_by,
            "updated_by": schedule.updated_by,
        }
