"""
传感器记录业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.sensorhistory_repository import SensorHistoryRepository
from ..repositories.sensor_repository import SensorRepository
from ..schemas.sensorhistory import SensorHistoryCreate, SensorHistoryUpdate, SensorHistoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class SensorHistoryService:
    """传感器记录业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.sensor_history_repo = SensorHistoryRepository(db)
        self.sensor_repo = SensorRepository(db)
    
    async def create_sensor_history(self, history_data: SensorHistoryCreate, user: dict) -> Dict[str, Any]:
        """创建传感器记录"""
        try:
            # 检查传感器是否存在
            sensor = await self.sensor_repo.get_by_id(history_data.sensor_id)
            if not sensor:
                raise ResourceNotFoundError(f"传感器ID '{history_data.sensor_id}' 不存在")
            
            create_data = history_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            history = await self.sensor_history_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_sensor_history",
                "success",
                f"创建传感器记录成功，ID: {history.id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_history_response(history),
                message="创建传感器记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建传感器记录失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建传感器记录失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的传感器不存在，请检查传感器ID是否正确")
            else:
                logger.error(f"创建传感器记录失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建传感器记录失败: {e}", exc_info=True)
            raise BusinessError(f"创建传感器记录失败: {str(e)}")
    
    async def get_sensor_history_by_id(self, history_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取传感器记录"""
        try:
            history = await self.sensor_history_repo.get_by_id(history_id)
            if not history:
                raise ResourceNotFoundError(f"传感器记录ID '{history_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_sensor_history_response(history),
                message="获取传感器记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取传感器记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取传感器记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器记录失败: {str(e)}")
    
    async def get_sensor_histories_by_ids(self, sensorhistory_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取传感器记录"""
        try:
            histories = await self.sensor_history_repo.get_by_ids(sensorhistory_ids)
            
            histories_data = [self._format_sensor_history_response(history) for history in histories]
            
            return ApiResponse.success(
                data={"sensor_histories": histories_data, "total": len(histories_data)},
                message="获取传感器记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器记录列表失败: {str(e)}")
    
    async def get_sensor_histories(self, query: SensorHistoryQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取传感器记录列表"""
        try:
            histories, total = await self.sensor_history_repo.get_all(
                page=query.page,
                size=query.size,
                sensor_id=query.sensor_id
            )
            
            # 格式化响应数据
            histories_data = [self._format_sensor_history_response(history) for history in histories]
            
            return ApiResponse.paginated(
                items=histories_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取传感器记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器记录列表失败: {str(e)}")
    
    async def update_sensor_history(self, history_id: str, history_data: SensorHistoryUpdate, user: dict) -> Dict[str, Any]:
        """更新传感器记录"""
        try:
            # 检查传感器记录是否存在
            existing_history = await self.sensor_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"传感器记录ID '{history_id}' 不存在")
            
            # 如果更新了传感器ID，检查传感器是否存在
            if history_data.sensor_id and history_data.sensor_id != existing_history.sensor_id:
                sensor = await self.sensor_repo.get_by_id(history_data.sensor_id)
                if not sensor:
                    raise ResourceNotFoundError(f"传感器ID '{history_data.sensor_id}' 不存在")
            
            update_data = history_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_history = await self.sensor_history_repo.update(history_id, update_data)
            
            log_user_action(
                user["username"],
                "update_sensor_history",
                "success",
                f"更新传感器记录成功，ID: {history_id}"
            )
            
            return ApiResponse.success(
                data=self._format_sensor_history_response(updated_history),
                message="更新传感器记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新传感器记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新传感器记录失败: {e}", exc_info=True)
            raise BusinessError(f"更新传感器记录失败: {str(e)}")
    
    async def delete_sensor_history(self, history_id: str, user: dict) -> Dict[str, Any]:
        """删除传感器记录"""
        try:
            # 检查传感器记录是否存在
            existing_history = await self.sensor_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"传感器记录ID '{history_id}' 不存在")
            
            # 删除传感器记录
            success = await self.sensor_history_repo.soft_delete(history_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_sensor_history",
                    "success",
                    f"删除传感器记录成功，ID: {history_id}"
                )
                
                return ApiResponse.success(
                    data={"history_id": history_id},
                    message="删除传感器记录成功"
                )
            else:
                raise BusinessError("删除传感器记录失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除传感器记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除传感器记录失败: {e}", exc_info=True)
            raise BusinessError(f"删除传感器记录失败: {str(e)}")
    
    async def get_sensor_history_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取传感器记录统计信息"""
        try:
            total_count = await self.sensor_history_repo.count_all()
            
            stats = {
                "total_histories": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取传感器记录统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取传感器记录统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取传感器记录统计失败: {str(e)}")
    
    def _format_sensor_history_response(self, history) -> Dict[str, Any]:
        """格式化传感器记录响应数据"""
        return {
            "id": history.id,
            "sensor_id": history.sensor_id,
            "record_data": history.record_data,
            "file_url": history.file_url,
            "created_at": history.created_at.strftime("%Y-%m-%dT%H:%M:%S") if history.created_at else None,
            "updated_at": history.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if history.updated_at else None,
            "created_by": history.created_by,
            "updated_by": history.updated_by,
        }
