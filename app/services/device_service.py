"""
设备业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.device_repository import DeviceRepository
from ..schemas.device import DeviceCreate, DeviceUpdate, DeviceQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class DeviceService:
    """设备业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
    
    async def create_device(self, device_data: DeviceCreate, user: dict) -> Dict[str, Any]:
        """创建设备"""
        try:
            # 检查设备名是否已存在
            if await self.device_repo.exists_by_name(device_data.device_name):
                raise BusinessError(f"设备名称 '{device_data.device_name}' 已存在")
            
            create_data = device_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            device = await self.device_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_device",
                "success",
                f"创建设备成功，ID: {device.id}"
            )
            
            return ApiResponse.success(
                data=self._format_device_response(device),
                message="创建设备成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建设备失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "Duplicate entry" in error_msg or "1062" in error_msg:
                logger.error(f"创建设备失败-唯一性约束错误: {error_msg}")
                raise BusinessError(f"设备名称 '{device_data.device_name}' 已存在")
            else:
                logger.error(f"创建设备失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建设备失败: {e}", exc_info=True)
            raise BusinessError(f"创建设备失败: {str(e)}")
    
    async def get_device_by_id(self, device_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取设备"""
        try:
            device = await self.device_repo.get_by_id(device_id)
            if not device:
                raise ResourceNotFoundError(f"设备ID '{device_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_device_response(device),
                message="获取设备成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取设备失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取设备失败: {e}", exc_info=True)
            raise BusinessError(f"获取设备失败: {str(e)}")
    
    async def get_devices_by_ids(self, device_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取设备"""
        try:
            devices = await self.device_repo.get_by_ids(device_ids)
            
            devices_data = [self._format_device_response(device) for device in devices]
            
            return ApiResponse.success(
                data={"devices": devices_data, "total": len(devices_data)},
                message="获取设备列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取设备列表失败: {str(e)}")
    
    async def get_devices(self, query: DeviceQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取设备列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                devices, total = await self.device_repo.get_all(
                    page=None,
                    size=None,
                    device_name=query.device_name,
                    map_id=query.map_id
                )
                devices_data = [self._format_device_response(device) for device in devices]
                return ApiResponse.success(
                    data={"items": devices_data, "total": total},
                    message="获取设备列表成功"
                )
            
            devices, total = await self.device_repo.get_all(
                page=query.page,
                size=query.size,
                device_name=query.device_name,
                map_id=query.map_id
            )
            
            # 格式化响应数据
            devices_data = [self._format_device_response(device) for device in devices]
            
            return ApiResponse.paginated(
                items=devices_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取设备列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取设备列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取设备列表失败: {str(e)}")
    
    async def update_device(self, device_id: str, device_data: DeviceUpdate, user: dict) -> Dict[str, Any]:
        """更新设备"""
        try:
            # 检查设备是否存在
            existing_device = await self.device_repo.get_by_id(device_id)
            if not existing_device:
                raise ResourceNotFoundError(f"设备ID '{device_id}' 不存在")
            
            # 如果更新了名称，检查是否重复
            if (device_data.device_name and 
                device_data.device_name != existing_device.device_name and
                await self.device_repo.exists_by_name(device_data.device_name, device_id)):
                raise BusinessError(f"设备名称 '{device_data.device_name}' 已存在")
            
            update_data = device_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_device = await self.device_repo.update(device_id, update_data)
            
            log_user_action(
                user["username"],
                "update_device",
                "success",
                f"更新设备成功，ID: {device_id}"
            )
            
            return ApiResponse.success(
                data=self._format_device_response(updated_device),
                message="更新设备成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新设备失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新设备失败: {e}", exc_info=True)
            raise BusinessError(f"更新设备失败: {str(e)}")
    
    async def delete_device(self, device_id: str, user: dict) -> Dict[str, Any]:
        """删除设备"""
        try:
            # 检查设备是否存在
            existing_device = await self.device_repo.get_by_id(device_id)
            if not existing_device:
                raise ResourceNotFoundError(f"设备ID '{device_id}' 不存在")
            
            # 删除设备
            success = await self.device_repo.soft_delete(device_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_device",
                    "success",
                    f"删除设备成功，ID: {device_id}"
                )
                
                return ApiResponse.success(
                    data={"id": device_id},
                    message="删除设备成功"
                )
            else:
                raise BusinessError("删除设备失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除设备失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除设备失败: {e}", exc_info=True)
            raise BusinessError(f"删除设备失败: {str(e)}")
    
    async def get_device_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取设备统计信息"""
        try:
            total_count = await self.device_repo.count_all()
            
            stats = {
                "total_devices": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取设备统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取设备统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取设备统计失败: {str(e)}")
    
    def _format_device_response(self, device) -> Dict[str, Any]:
        """格式化设备响应数据"""
        return {
            "id": device.id,
            "device_name": device.device_name,
            "device_params": device.device_params,
            "map_id": device.map_id,
            "x_coordinate": device.x_coordinate,
            "y_coordinate": device.y_coordinate,
            "created_at": device.created_at.strftime("%Y-%m-%dT%H:%M:%S") if device.created_at else None,
            "updated_at": device.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if device.updated_at else None,
            "created_by": device.created_by,
            "updated_by": device.updated_by,
        }

