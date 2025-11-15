"""
地图业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.map_repository import MapRepository
from ..schemas.map import MapCreate, MapUpdate, MapQuery
from ..core.exceptions import (
    ValidationError, BusinessError, ResourceNotFoundError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action
import uuid
from datetime import datetime

logger = get_logger(__name__)


class MapService:
    """地图业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.map_repo = MapRepository(db)
    
    def _format_map_response(self, map_obj) -> dict:
        """格式化地图响应数据"""
        return {
            "id": map_obj.id,
            "map_name": map_obj.map_name,
            "map_image_url": map_obj.map_image_url,
            "map_scale": float(map_obj.map_scale) if map_obj.map_scale is not None else None,
            "map_center_x": float(map_obj.map_center_x) if map_obj.map_center_x is not None else None,
            "map_center_y": float(map_obj.map_center_y) if map_obj.map_center_y is not None else None,
            "factory_id": map_obj.factory_id,
            "created_at": map_obj.created_at,
            "updated_at": map_obj.updated_at,
            "created_by": map_obj.created_by,
            "updated_by": map_obj.updated_by
        }
    
    async def create_map(self, map_data: MapCreate, user: dict) -> Dict[str, Any]:
        """创建地图"""
        try:
            # 检查地图名是否已存在
            if await self.map_repo.exists_by_name_global(map_data.map_name):
                raise BusinessError(f"地图名称 '{map_data.map_name}' 已存在")
            
            # 准备创建数据
            create_data = {
                "id": str(uuid.uuid4()),
                **map_data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }
            
            # 创建地图
            map_obj = await self.map_repo.create(create_data)
            
            # 记录业务日志
            log_user_action(
                user=user["username"],
                action="创建地图",
                result="成功",
                details=f"地图名称: {map_data.map_name}"
            )
            
            logger.info(
                "用户创建地图成功",
                extra={
                    "user_id": user["id"],
                    "map_id": map_obj.id,
                    "map_name": map_data.map_name
                }
            )
            
            return ApiResponse.success(
                data={"map": self._format_map_response(map_obj)},
                message="地图创建成功"
            )
            
        except Exception as e:
            logger.error(
                "创建地图失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_name": map_data.map_name
                },
                exc_info=True
            )
            raise
    
    async def get_map_by_id(self, map_id: str, user: Optional[dict] = None) -> Dict[str, Any]:
        """根据ID获取地图详情"""
        map_obj = await self.map_repo.get_by_id(map_id)
        if not map_obj:
            raise ResourceNotFoundError(f"地图 '{map_id}' 不存在")
        
        return ApiResponse.success(data={"map": self._format_map_response(map_obj)})
    
    async def get_user_maps(self, query: MapQuery, user: dict) -> Dict[str, Any]:
        """获取所有地图列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                maps, total = await self.map_repo.get_all(
                    map_name=query.map_name,
                    skip=None,
                    limit=None
                )
                maps_dict = [self._format_map_response(map_obj) for map_obj in maps]
                return ApiResponse.success(
                    data={"items": maps_dict, "total": total},
                    message="获取地图列表成功"
                )
            
            # 计算分页参数
            skip = (query.page - 1) * query.size
            
            # 查询所有地图数据
            maps, total = await self.map_repo.get_all(
                map_name=query.map_name,
                skip=skip,
                limit=query.size
            )
            
            # 转换地图列表为字典列表
            maps_dict = [self._format_map_response(map_obj) for map_obj in maps]
            
            return ApiResponse.paginated(
                items=maps_dict,
                total=total,
                page=query.page,
                size=query.size
            )
            
        except Exception as e:
            logger.error(
                "获取用户地图列表失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "query": query.dict()
                },
                exc_info=True
            )
            raise
    
    async def update_map(self, map_id: str, map_data: MapUpdate, user: dict) -> Dict[str, Any]:
        """更新地图"""
        try:
            # 检查地图是否存在
            existing_map = await self.map_repo.get_by_id(map_id)
            if not existing_map:
                raise ResourceNotFoundError(f"地图 '{map_id}' 不存在")
            
            # 如果更新地图名，检查是否与其他地图重名
            if (map_data.map_name and 
                map_data.map_name != existing_map.map_name and
                await self.map_repo.exists_by_name_global(map_data.map_name, map_id)):
                raise BusinessError(f"地图名称 '{map_data.map_name}' 已存在")
            
            # 准备更新数据（只更新已设置的字段，包括0值）
            update_data = {}
            for field, value in map_data.dict(exclude_unset=True).items():
                # 对于数字字段，0是有效值，不应该被过滤
                update_data[field] = value
            
            if update_data:
                update_data["updated_by"] = user["username"]
                
                # 更新地图
                map_obj = await self.map_repo.update(map_id, user["id"], update_data)
                
                # 记录业务日志
                log_user_action(
                    user=user["username"],
                    action="更新地图",
                    result="成功",
                    details=f"地图ID: {map_id}, 更新字段: {list(update_data.keys())}"
                )
                
                logger.info(
                    "用户更新地图成功",
                    extra={
                        "user_id": user["id"],
                        "map_id": map_id,
                        "updated_fields": list(update_data.keys())
                    }
                )
                
                return ApiResponse.success(
                    data={"map": self._format_map_response(map_obj)},
                    message="地图更新成功"
                )
            else:
                return ApiResponse.success(
                    data={"map": self._format_map_response(existing_map)},
                    message="无需更新"
                )
                
        except Exception as e:
            logger.error(
                "更新地图失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_id": map_id,
                    "update_data": map_data.dict()
                },
                exc_info=True
            )
            raise
    
    async def delete_map(self, map_id: str, user: dict) -> Dict[str, Any]:
        """删除地图"""
        try:
            # 检查地图是否存在
            existing_map = await self.map_repo.get_by_id(map_id)
            if not existing_map:
                raise ResourceNotFoundError(f"地图 '{map_id}' 不存在")
            
            # 软删除地图
            success = await self.map_repo.soft_delete(map_id, user["username"])
            
            if success:
                # 记录业务日志
                log_user_action(
                    user=user["username"],
                    action="删除地图",
                    result="成功",
                    details=f"地图名称: {existing_map.map_name}"
                )
                
                logger.info(
                    "用户删除地图成功",
                    extra={
                        "user_id": user["id"],
                        "map_id": map_id,
                        "map_name": existing_map.map_name
                    }
                )
                
                return ApiResponse.success(
                    data={"id": map_id},
                    message="地图删除成功"
                )
            else:
                raise BusinessError("地图删除失败")
                
        except Exception as e:
            logger.error(
                "删除地图失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_id": map_id
                },
                exc_info=True
            )
            raise
    
    async def get_map_stats(self, user: dict) -> Dict[str, Any]:
        """获取用户地图统计信息"""
        try:
            total_count = await self.map_repo.count_by_user(user["id"])
            
            return ApiResponse.success(
                data={
                    "total_maps": total_count,
                    "user_id": user["id"]
                },
                message="获取地图统计成功"
            )
            
        except Exception as e:
            logger.error(
                "获取地图统计失败: %s",
                str(e),
                extra={"user_id": user["id"]},
                exc_info=True
            )
            raise

    def _format_robot_response(self, robot) -> Dict[str, Any]:
        """格式化机器人响应数据"""
        return {
            "id": robot.id,
            "robot_name": robot.robot_name,
            "robot_info": robot.robot_info,
            "factory_id": robot.factory_id,
            "created_at": robot.created_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.created_at else None,
            "updated_at": robot.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if robot.updated_at else None,
            "created_by": robot.created_by,
            "updated_by": robot.updated_by,
        }

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
                            "created_at": sensor.created_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.created_at else None,
                            "updated_at": sensor.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if sensor.updated_at else None,
                        })
                
                devices_data.append({
                    "id": device.id,
                    "device_name": device.device_name,
                    "device_params": device.device_params,
                    "point_id": device.point_id,
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
            "x_coordinate": point.x_coordinate,
            "y_coordinate": point.y_coordinate,
            "devices": devices_data,
            "created_at": point.created_at.strftime("%Y-%m-%dT%H:%M:%S") if point.created_at else None,
            "updated_at": point.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if point.updated_at else None,
            "created_by": point.created_by,
            "updated_by": point.updated_by,
        }

    async def get_map_with_robots_points_items(self, map_id: str, user: Optional[dict] = None) -> Dict[str, Any]:
        """获取地图及其关联的机器人、巡检点和巡检项目数据"""
        try:
            # 获取地图及其关联数据
            related_data = await self.map_repo.get_map_with_related_data(map_id)
            
            if not related_data:
                raise ResourceNotFoundError(f"地图 '{map_id}' 不存在")
            
            # 格式化响应数据
            result = {
                "map": self._format_map_response(related_data["map"]),
                "robots": [self._format_robot_response(robot) for robot in related_data["robots"]],
                "points": [self._format_point_response(point) for point in related_data["points"]]
            }
            
            return ApiResponse.success(
                data=result,
                message="获取地图关联数据成功"
            )
            
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(
                "获取地图关联数据失败: %s",
                str(e),
                extra={"map_id": map_id},
                exc_info=True
            )
            raise BusinessError(f"获取地图关联数据失败: {str(e)}")
