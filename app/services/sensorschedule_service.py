"""
传感器日程业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.sensorschedule_repository import SensorScheduleRepository
from ..repositories.sensor_repository import SensorRepository
from ..schemas.sensorschedule import SensorScheduleCreate, SensorScheduleUpdate, SensorScheduleQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class SensorScheduleService:
    """传感器日程业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sensor_schedule_repo = SensorScheduleRepository(db)
        self.sensor_repo = SensorRepository(db)
    
    async def create_sensor_schedule(self, schedule_data: SensorScheduleCreate, user: dict) -> Dict[str, Any]:
        """创建传感器日程"""
        try:
            # 检查传感器是否存在
            sensor = await self.sensor_repo.get_by_id(schedule_data.sensor_id)
            if not sensor:
                raise ResourceNotFoundError(f"传感器ID '{schedule_data.sensor_id}' 不存在")
            
            create_data = schedule_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            schedule = await self.sensor_schedule_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_sensor_schedule",
                "success",
                f"创建传感器日程成功，ID: {schedule.id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_schedule_response(schedule),
                message="创建传感器日程成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建传感器日程失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建传感器日程失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的传感器不存在，请检查传感器ID是否正确")
            elif "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建传感器日程失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"传感器日程名称 '{schedule_data.schedule_name}' 已存在")
            else:
                logger.error(f"创建传感器日程失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建传感器日程失败: {e}", exc_info=True)
            raise BusinessError(f"创建传感器日程失败: {str(e)}")
    
    async def get_sensor_schedule_by_id(self, schedule_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取传感器日程"""
        try:
            schedule = await self.sensor_schedule_repo.get_by_id(schedule_id)
            if not schedule:
                raise ResourceNotFoundError(f"传感器日程ID '{schedule_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_sensor_schedule_response(schedule),
                message="获取传感器日程成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取传感器日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取传感器日程失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器日程失败: {str(e)}")
    
    async def get_sensor_schedules_by_ids(self, sensorschedule_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取传感器日程"""
        try:
            schedules = await self.sensor_schedule_repo.get_by_ids(sensorschedule_ids)
            
            schedules_data = [self._format_sensor_schedule_response(schedule) for schedule in schedules]
            
            return ApiResponse.success(
                data={"sensor_schedules": schedules_data, "total": len(schedules_data)},
                message="获取传感器日程列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器日程列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器日程列表失败: {str(e)}")
    
    async def get_sensor_schedules(self, query: SensorScheduleQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取传感器日程列表"""
        try:
            schedules, total = await self.sensor_schedule_repo.get_all(
                page=query.page,
                size=query.size,
                schedule_type=query.schedule_type,
                schedule_is_active=query.schedule_is_active,
                sensor_id=query.sensor_id
            )
            
            # 格式化响应数据
            schedules_data = [self._format_sensor_schedule_response(schedule) for schedule in schedules]
            
            return ApiResponse.paginated(
                items=schedules_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取传感器日程列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器日程列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器日程列表失败: {str(e)}")
    
    async def update_sensor_schedule(self, schedule_id: str, schedule_data: SensorScheduleUpdate, user: dict) -> Dict[str, Any]:
        """更新传感器日程"""
        try:
            # 检查传感器日程是否存在
            existing_schedule = await self.sensor_schedule_repo.get_by_id(schedule_id)
            if not existing_schedule:
                raise ResourceNotFoundError(f"传感器日程ID '{schedule_id}' 不存在")
            
            # 如果更新了传感器ID，检查传感器是否存在
            if schedule_data.sensor_id and schedule_data.sensor_id != existing_schedule.sensor_id:
                sensor = await self.sensor_repo.get_by_id(schedule_data.sensor_id)
                if not sensor:
                    raise ResourceNotFoundError(f"传感器ID '{schedule_data.sensor_id}' 不存在")
            
            update_data = schedule_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_schedule = await self.sensor_schedule_repo.update(schedule_id, update_data)
            
            log_user_action(
                user["username"],
                "update_sensor_schedule",
                "success",
                f"更新传感器日程成功，ID: {schedule_id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_schedule_response(updated_schedule),
                message="更新传感器日程成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新传感器日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新传感器日程失败: {e}", exc_info=True)
            raise BusinessError(f"更新传感器日程失败: {str(e)}")
    
    async def delete_sensor_schedule(self, schedule_id: str, user: dict) -> Dict[str, Any]:
        """删除传感器日程"""
        try:
            # 检查传感器日程是否存在
            existing_schedule = await self.sensor_schedule_repo.get_by_id(schedule_id)
            if not existing_schedule:
                raise ResourceNotFoundError(f"传感器日程ID '{schedule_id}' 不存在")
            
            # 删除传感器日程
            success = await self.sensor_schedule_repo.soft_delete(schedule_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_sensor_schedule",
                    "success",
                    f"删除传感器日程成功，ID: {schedule_id}"
                )
                
                return ApiResponse.success(
                    data={"schedule_id": schedule_id},
                    message="删除传感器日程成功"
                )
            else:
                raise BusinessError("删除传感器日程失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除传感器日程失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除传感器日程失败: {e}", exc_info=True)
            raise BusinessError(f"删除传感器日程失败: {str(e)}")
    
    async def get_sensor_schedule_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取传感器日程统计信息"""
        try:
            total_count = await self.sensor_schedule_repo.count_all()
            active_count = await self.sensor_schedule_repo.count_active()
            
            stats = {
                "total_schedules": total_count,
                "active_schedules": active_count,
                "inactive_schedules": total_count - active_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取传感器日程统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器日程统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器日程统计失败: {str(e)}")
    
    def _format_sensor_schedule_response(self, schedule) -> Dict[str, Any]:
        """格式化传感器日程响应数据"""
        return {
            "id": schedule.id,
            "schedule_type": schedule.schedule_type,
            "schedule_is_active": schedule.schedule_is_active,
            "sensor_id": schedule.sensor_id,
            "schedule_param": schedule.schedule_param,
            "set_time": schedule.set_time,
            "created_at": schedule.created_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.created_at else None,
            "updated_at": schedule.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if schedule.updated_at else None,
            "created_by": schedule.created_by,
            "updated_by": schedule.updated_by,
        }
