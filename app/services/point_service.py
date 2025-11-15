"""
巡检点业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.point_repository import PointRepository
from ..repositories.map_repository import MapRepository
from ..schemas.point import PointCreate, PointUpdate, PointResponse, PointListResponse
from ..core.exceptions import ResourceNotFoundError, PermissionDeniedError
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class PointService:
    """巡检点业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.point_repo = PointRepository(db)
        self.map_repo = MapRepository(db)
    
    def _format_point_response(self, point) -> Dict[str, Any]:
        """格式化巡检点响应数据（包含设备和巡检项目）"""
        # 格式化设备数据
        devices_data = []
        if hasattr(point, 'devices') and point.devices:
            for device in point.devices:
                # 格式化设备下的巡检项目
                items_data = []
                if hasattr(device, 'items') and device.items:
                    for item in device.items:
                        items_data.append({
                            "id": item.id,
                            "item_name": item.item_name,
                            "item_info": item.item_info,
                            "device_id": item.device_id,
                            "enabled": item.enabled,
                            "created_at": item.created_at.strftime("%Y-%m-%dT%H:%M:%S") if item.created_at else None,
                            "updated_at": item.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if item.updated_at else None,
                        })
                
                # 格式化设备下的传感器
                sensors_data = []
                if hasattr(device, 'sensors') and device.sensors:
                    for sensor in device.sensors:
                        sensors_data.append({
                            "id": sensor.id,
                            "sensor_name": sensor.sensor_name,
                            "sensor_params": sensor.sensor_params,
                            "device_id": sensor.device_id,
                            "enabled": sensor.enabled,
                            "created_at": sensor.created_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.created_at else None,
                            "updated_at": sensor.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.updated_at else None,
                        })
                
                devices_data.append({
                    "id": device.id,
                    "device_name": device.device_name,
                    "device_params": device.device_params,
                    "point_id": device.point_id,
                    "enabled": device.enabled,
                    "x_coordinate": device.x_coordinate,
                    "y_coordinate": device.y_coordinate,
                    "items": items_data,
                    "sensors": sensors_data,
                    "created_at": device.created_at.strftime("%Y-%m-%dT%H:%M:%S") if device.created_at else None,
                    "updated_at": device.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if device.updated_at else None,
                })
        
        return {
            "id": point.id,
            "point_name": point.point_name,
            "map_id": point.map_id,
            "enabled": point.enabled,
            "x_coordinate": point.x_coordinate,
            "y_coordinate": point.y_coordinate,
            "devices": devices_data,
            "created_at": point.created_at.strftime("%Y-%m-%dT%H:%M:%S") if point.created_at else None,
            "updated_at": point.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if point.updated_at else None,
            "created_by": point.created_by,
            "updated_by": point.updated_by,
        }
    
    async def create_point(self, point_data: PointCreate, user: dict) -> Dict[str, Any]:
        """创建巡检点"""
        try:
            # 检查地图是否存在且用户有权限
            map_obj = await self.map_repo.get_by_id(point_data.map_id)
            if not map_obj:
                raise ResourceNotFoundError(f"地图 '{point_data.map_id}' 不存在")
            
            
            create_data = point_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            point = await self.point_repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "create_point",
                "success",
                f"创建巡检点成功，ID: {point.id}"
            )
            
            return ApiResponse.success(
                data=self._format_point_response(point),
                message="创建巡检点成功"
            )
            
        except Exception as e:
            logger.error(f"创建巡检点失败: {e}")
            log_user_action(
                user["username"],
                "create_point",
                "failed",
                f"创建巡检点失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="创建巡检点失败")
    
    async def get_point_by_id(self, point_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取巡检点"""
        point = await self.point_repo.get_by_id(point_id)
        if not point:
            raise ResourceNotFoundError(f"巡检点 '{point_id}' 不存在")
        
        
        return ApiResponse.success(
            data=self._format_point_response(point),
            message="获取巡检点成功"
        )
    
    async def get_points_by_ids(self, point_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取巡检点"""
        try:
            points = await self.point_repo.get_by_ids(point_ids)
            
            items_data = [self._format_point_response(point) for point in points]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取巡检点列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检点列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检点列表失败")
    
    async def get_points(self, user: dict, page: Optional[int] = None, size: Optional[int] = None, point_name: str = None, map_id: str = None) -> Dict[str, Any]:
        """获取巡检点列表"""
        try:
            # 如果指定了map_id，检查地图是否存在
            if map_id:
                map_obj = await self.map_repo.get_by_id(map_id)
                if not map_obj:
                    raise ResourceNotFoundError(f"地图 '{map_id}' 不存在")
            
            # 如果未提供分页参数，返回所有数据
            if page is None or size is None:
                points, total = await self.point_repo.get_all(None, None, point_name, map_id)
                items = [self._format_point_response(point) for point in points]
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取巡检点列表成功"
                )
            
            points, total = await self.point_repo.get_all(page, size, point_name, map_id)
            
            # 格式化响应数据
            items = [self._format_point_response(point) for point in points]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=page,
                size=size,
                message="获取巡检点列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检点列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检点列表失败")
    
    async def update_point(self, point_id: str, point_data: PointUpdate, user: dict) -> Dict[str, Any]:
        """更新巡检点"""
        # 检查巡检点是否存在
        point = await self.point_repo.get_by_id(point_id)
        if not point:
            raise ResourceNotFoundError(f"巡检点 '{point_id}' 不存在")
        
        # 检查权限
        
        try:
            # 准备更新数据
            update_data = point_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            # 更新巡检点
            updated_point = await self.point_repo.update(point_id, update_data)
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "update_point",
                "success",
                f"更新巡检点成功，ID: {point_id}"
            )
            
            return ApiResponse.success(
                data=self._format_point_response(updated_point),
                message="更新巡检点成功"
            )
            
        except Exception as e:
            logger.error(f"更新巡检点失败: {e}")
            log_user_action(
                user["username"],
                "update_point",
                "failed",
                f"更新巡检点失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="更新巡检点失败")
    
    async def delete_point(self, point_id: str, user: dict) -> Dict[str, Any]:
        """删除巡检点（级联删除关联关系）"""
        # 检查巡检点是否存在
        point = await self.point_repo.get_by_id(point_id)
        if not point:
            raise ResourceNotFoundError(f"巡检点 '{point_id}' 不存在")
        
        try:
            # 软删除巡检点（设备和巡检项目会通过CASCADE自动级联删除）
            success = await self.point_repo.soft_delete(point_id)
            if not success:
                raise HTTPException(status_code=500, detail="删除巡检点失败")
            
            # 记录操作日志
            log_user_action(
                user["username"],
                "delete_point",
                "success",
                f"删除巡检点成功，ID: {point_id}"
            )
            
            return ApiResponse.success(
                data={
                    "point_id": point_id
                },
                message="删除巡检点成功"
            )
            
        except Exception as e:
            logger.error(f"删除巡检点失败: {e}")
            log_user_action(
                user["username"],
                "delete_point",
                "failed",
                f"删除巡检点失败: {str(e)}"
            )
            raise HTTPException(status_code=500, detail="删除巡检点失败")
    
    async def get_point_stats(self, user: dict) -> Dict[str, Any]:
        """获取巡检点统计信息"""
        try:
            total_count = await self.point_repo.count_all()
            
            stats = {
                "total_points": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取巡检点统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检点统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检点统计失败")
