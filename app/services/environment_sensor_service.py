"""
环境传感器业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.environmentsensor_repository import EnvironmentSensorRepository
from ..schemas.environmentsensor import EnvironmentSensorCreate, EnvironmentSensorUpdate, EnvironmentSensorQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class EnvironmentSensorService:
    """环境传感器业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = EnvironmentSensorRepository(db)

    async def create_sensor(self, data: EnvironmentSensorCreate, user: dict) -> Dict[str, Any]:
        """创建环境传感器"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建环境传感器
            sensor = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_environment_sensor",
                f"创建环境传感器: 站号{sensor.station_number}, 波特率{sensor.baud_rate}",
                extra={"sensor_id": sensor.id, "station_number": sensor.station_number, "baud_rate": sensor.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_sensor_response(sensor),
                message="环境传感器创建成功"
            )

        except Exception as e:
            logger.error(f"创建环境传感器失败: {e}", exc_info=True)
            raise BusinessError(f"创建环境传感器失败: {str(e)}")

    async def get_sensor_by_id(self, sensor_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取环境传感器"""
        try:
            sensor = await self.repo.get_by_id(sensor_id)
            if not sensor:
                raise ResourceNotFoundError(f"环境传感器ID '{sensor_id}' 不存在")

            return ApiResponse.success(
                data=self._format_sensor_response(sensor),
                message="获取环境传感器成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取环境传感器失败: {e}", exc_info=True)
            raise BusinessError(f"获取环境传感器失败: {str(e)}")

    async def get_sensors_by_ids(self, environmentsensor_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取环境传感器"""
        try:
            sensors = await self.repo.get_by_ids(environmentsensor_ids)
            if not sensors:
                raise ResourceNotFoundError("未找到任何环境传感器")

            return ApiResponse.success(
                data=[self._format_sensor_response(sensor) for sensor in sensors],
                message=f"成功获取 {len(sensors)} 个环境传感器"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"批量获取环境传感器失败: {e}", exc_info=True)
            raise BusinessError(f"批量获取环境传感器失败: {str(e)}")

    async def get_sensors(self, query: EnvironmentSensorQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取环境传感器列表"""
        try:
            sensors, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                station_number=query.station_number,
                baud_rate=query.baud_rate
            )

            return ApiResponse.paginated(
                items=[self._format_sensor_response(sensor) for sensor in sensors],
                total=total,
                page=query.page,
                size=query.size,
                message="获取环境传感器列表成功"
            )

        except Exception as e:
            logger.error(f"获取环境传感器列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取环境传感器列表失败: {str(e)}")

    async def update_sensor(self, sensor_id: str, data: EnvironmentSensorUpdate, user: dict) -> Dict[str, Any]:
        """更新环境传感器"""
        try:
            # 检查环境传感器是否存在
            existing_sensor = await self.repo.get_by_id(sensor_id)
            if not existing_sensor:
                raise ResourceNotFoundError(f"环境传感器ID '{sensor_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新环境传感器
            sensor = await self.repo.update(sensor_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_environment_sensor",
                f"更新环境传感器: 站号{sensor.station_number}, 波特率{sensor.baud_rate}",
                extra={"sensor_id": sensor.id, "station_number": sensor.station_number, "baud_rate": sensor.baud_rate}
            )

            return ApiResponse.success(
                data=self._format_sensor_response(sensor),
                message="环境传感器更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新环境传感器失败: {e}", exc_info=True)
            raise BusinessError(f"更新环境传感器失败: {str(e)}")

    async def delete_sensor(self, sensor_id: str, user: dict) -> Dict[str, Any]:
        """删除环境传感器"""
        try:
            # 检查环境传感器是否存在
            existing_sensor = await self.repo.get_by_id(sensor_id)
            if not existing_sensor:
                raise ResourceNotFoundError(f"环境传感器ID '{sensor_id}' 不存在")

            # 软删除环境传感器
            success = await self.repo.soft_delete(sensor_id, user["username"])
            if not success:
                raise BusinessError("删除环境传感器失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_environment_sensor",
                f"删除环境传感器: 站号{existing_sensor.station_number}, 波特率{existing_sensor.baud_rate}",
                extra={"sensor_id": sensor_id, "station_number": existing_sensor.station_number, "baud_rate": existing_sensor.baud_rate}
            )

            return ApiResponse.success(
                data={"id": sensor_id},
                message="环境传感器删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除环境传感器失败: {e}", exc_info=True)
            raise BusinessError(f"删除环境传感器失败: {str(e)}")

    async def get_sensor_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取环境传感器统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取环境传感器统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取环境传感器统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取环境传感器统计信息失败: {str(e)}")

    def _format_sensor_response(self, sensor) -> Dict[str, Any]:
        """格式化环境传感器响应数据"""
        return {
            "id": sensor.id,
            "robot_id": sensor.robot_id,
            "station_number": sensor.station_number,
            "baud_rate": sensor.baud_rate,
            "created_at": sensor.created_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.created_at else None,
            "updated_at": sensor.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.updated_at else None,
            "created_by": sensor.created_by,
            "updated_by": sensor.updated_by,
        }

