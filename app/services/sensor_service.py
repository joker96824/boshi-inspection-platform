"""
智能传感器业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.sensor_repository import SensorRepository
from ..repositories.device_repository import DeviceRepository
from ..schemas.sensor import SensorCreate, SensorUpdate, SensorQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class SensorService:
    """智能传感器业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sensor_repo = SensorRepository(db)
        self.device_repo = DeviceRepository(db)
    
    async def create_sensor(self, sensor_data: SensorCreate, user: dict) -> Dict[str, Any]:
        """创建智能传感器"""
        try:
            # 检查设备是否存在
            device = await self.device_repo.get_by_id(sensor_data.device_id)
            if not device:
                raise ResourceNotFoundError(f"设备ID '{sensor_data.device_id}' 不存在")
            
            create_data = sensor_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            sensor = await self.sensor_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_sensor",
                "success",
                f"创建智能传感器成功，ID: {sensor.id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_response(sensor),
                message="创建智能传感器成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建智能传感器失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建智能传感器失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的设备不存在，请检查设备ID是否正确")
            elif "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建智能传感器失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"智能传感器名称 '{sensor_data.sensor_name}' 已存在")
            else:
                logger.error(f"创建智能传感器失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建智能传感器失败: {e}", exc_info=True)
            raise BusinessError(f"创建智能传感器失败: {str(e)}")
    
    async def get_sensor_by_id(self, sensor_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取智能传感器"""
        try:
            sensor = await self.sensor_repo.get_by_id(sensor_id)
            if not sensor:
                raise ResourceNotFoundError(f"智能传感器ID '{sensor_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_sensor_response(sensor),
                message="获取智能传感器成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取智能传感器失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取智能传感器失败: {e}", exc_info=True)
            raise BusinessError(f"获取智能传感器失败: {str(e)}")
    
    async def get_sensors_by_ids(self, sensor_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取智能传感器"""
        try:
            sensors = await self.sensor_repo.get_by_ids(sensor_ids)
            
            sensors_data = [self._format_sensor_response(sensor) for sensor in sensors]
            
            return ApiResponse.success(
                data={"sensors": sensors_data, "total": len(sensors_data)},
                message="获取智能传感器列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取智能传感器列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取智能传感器列表失败: {str(e)}")
    
    async def get_sensors(self, query: SensorQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取智能传感器列表"""
        try:
            sensors, total = await self.sensor_repo.get_all(
                page=query.page,
                size=query.size,
                sensor_name=query.sensor_name,
                device_id=query.device_id
            )
            
            # 格式化响应数据
            sensors_data = [self._format_sensor_response(sensor) for sensor in sensors]
            
            return ApiResponse.paginated(
                items=sensors_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取智能传感器列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取智能传感器列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取智能传感器列表失败: {str(e)}")
    
    async def update_sensor(self, sensor_id: str, sensor_data: SensorUpdate, user: dict) -> Dict[str, Any]:
        """更新智能传感器"""
        try:
            # 检查智能传感器是否存在
            existing_sensor = await self.sensor_repo.get_by_id(sensor_id)
            if not existing_sensor:
                raise ResourceNotFoundError(f"智能传感器ID '{sensor_id}' 不存在")
            
            # 如果更新了设备ID，检查设备是否存在
            if sensor_data.device_id and sensor_data.device_id != existing_sensor.device_id:
                device = await self.device_repo.get_by_id(sensor_data.device_id)
                if not device:
                    raise ResourceNotFoundError(f"设备ID '{sensor_data.device_id}' 不存在")
            
            update_data = sensor_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_sensor = await self.sensor_repo.update(sensor_id, update_data)
            
            log_user_action(
                user["username"],
                "update_sensor",
                "success",
                f"更新智能传感器成功，ID: {sensor_id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_response(updated_sensor),
                message="更新智能传感器成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新智能传感器失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新智能传感器失败: {e}", exc_info=True)
            raise BusinessError(f"更新智能传感器失败: {str(e)}")
    
    async def delete_sensor(self, sensor_id: str, user: dict) -> Dict[str, Any]:
        """删除智能传感器"""
        try:
            # 检查智能传感器是否存在
            existing_sensor = await self.sensor_repo.get_by_id(sensor_id)
            if not existing_sensor:
                raise ResourceNotFoundError(f"智能传感器ID '{sensor_id}' 不存在")
            
            # 删除智能传感器
            success = await self.sensor_repo.soft_delete(sensor_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_sensor",
                    "success",
                    f"删除智能传感器成功，ID: {sensor_id}"
                )
                
                return ApiResponse.success(
                    data={"id": sensor_id},
                    message="删除智能传感器成功"
                )
            else:
                raise BusinessError("删除智能传感器失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除智能传感器失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除智能传感器失败: {e}", exc_info=True)
            raise BusinessError(f"删除智能传感器失败: {str(e)}")
    
    async def get_sensor_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取智能传感器统计信息"""
        try:
            total_count = await self.sensor_repo.count_all()
            
            stats = {
                "total_sensors": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取智能传感器统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取智能传感器统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取智能传感器统计失败: {str(e)}")
    
    def _format_sensor_response(self, sensor) -> Dict[str, Any]:
        """格式化智能传感器响应数据"""
        # 格式化分组信息
        group_info = None
        if sensor.group and not sensor.group.is_deleted:
            group_info = {
                "id": sensor.group.id,
                "group_name": sensor.group.group_name,
                "group_description": sensor.group.group_description,
            }
        
        return {
            "id": sensor.id,
            "device_id": sensor.device_id,
            "sensor_name": sensor.sensor_name,
            "sensor_params": sensor.sensor_params,
            "group_id": sensor.group_id,
            "group": group_info,
            "enabled": sensor.enabled,
            "created_at": sensor.created_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.created_at else None,
            "updated_at": sensor.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.updated_at else None,
            "created_by": sensor.created_by,
            "updated_by": sensor.updated_by,
        }
    
    async def batch_update_group(self, sensor_ids: List[str], group_id: Optional[str], user: dict) -> Dict[str, Any]:
        """批量更新传感器分组"""
        from ..repositories.group_repository import GroupRepository
        
        try:
            # 如果提供了group_id，验证分组是否存在
            if group_id is not None:
                group_repo = GroupRepository(self.db)
                group = await group_repo.get_by_id(group_id)
                if not group:
                    raise ResourceNotFoundError(f"分组 '{group_id}' 不存在")
            
            # 批量更新
            updated_count = await self.sensor_repo.batch_update_group(
                sensor_ids=sensor_ids,
                group_id=group_id,
                updated_by=user["username"]
            )
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "batch_update_sensor_group",
                "success",
                f"批量更新传感器分组成功，更新数量: {updated_count}"
            )
            
            return ApiResponse.success(
                data={"updated_count": updated_count},
                message=f"批量更新传感器分组成功，共更新 {updated_count} 个传感器"
            )
            
        except Exception as e:
            logger.error(f"批量更新传感器分组失败: {e}", exc_info=True)
            log_user_action(
                user["username"],
                "batch_update_sensor_group",
                "failed",
                f"批量更新传感器分组失败: {str(e)}"
            )
            raise BusinessError(f"批量更新传感器分组失败: {str(e)}")

