"""
地图路网业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from ..repositories.mapnet_repository import MapNetRepository
from ..schemas.mapnet import MapNetCreate, MapNetUpdate, MapNetQuery
from ..core.exceptions import (
    ValidationError, BusinessError, ResourceNotFoundError, PermissionDeniedError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action
import uuid

logger = get_logger(__name__)


class MapNetService:
    """地图路网业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.mapnet_repo = MapNetRepository(db)
    
    def _format_mapnet_response(self, mapnet_obj) -> dict:
        """格式化地图路网响应数据"""
        return {
            "id": mapnet_obj.id,
            "map_id": mapnet_obj.map_id,
            "map_net_type": mapnet_obj.map_net_type,
            "map_net_properties": mapnet_obj.map_net_properties,
            "map_net_geometry": mapnet_obj.map_net_geometry,
            "created_at": mapnet_obj.created_at,
            "updated_at": mapnet_obj.updated_at,
            "created_by": mapnet_obj.created_by,
            "updated_by": mapnet_obj.updated_by
        }
    
    async def create_mapnet(self, mapnet_data: MapNetCreate, user: dict) -> Dict[str, Any]:
        """创建地图路网元素"""
        try:
            # 地图存在性检查已完成，无需额外权限检查
            
            # 准备创建数据
            create_data = {
                "id": str(uuid.uuid4()),
                **mapnet_data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }
            
            # 创建路网元素
            mapnet_obj = await self.mapnet_repo.create(create_data)
            
            # 记录业务日志
            log_user_action(
                user=user["username"],
                action="创建路网元素",
                result="成功",
                details=f"地图ID: {mapnet_data.map_id}, 元素类型: {mapnet_data.map_net_type}"
            )
            
            logger.info(
                "用户创建路网元素成功",
                extra={
                    "user_id": user["id"],
                    "mapnet_id": mapnet_obj.id,
                    "map_id": mapnet_data.map_id,
                    "map_net_type": mapnet_data.map_net_type
                }
            )
            
            return ApiResponse.success(
                data={"mapnet": self._format_mapnet_response(mapnet_obj)},
                message="路网元素创建成功"
            )
            
        except Exception as e:
            logger.error(
                "创建路网元素失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_id": mapnet_data.map_id,
                    "map_net_type": mapnet_data.map_net_type
                },
                exc_info=True
            )
            raise
    
    async def get_mapnet_by_id(self, mapnet_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取路网元素详情"""
        mapnet_obj = await self.mapnet_repo.get_by_id(mapnet_id)
        if not mapnet_obj:
            raise ResourceNotFoundError(f"路网元素 '{mapnet_id}' 不存在")
        
        # 路网元素存在性检查已完成，无需额外权限检查
        
        return ApiResponse.success(data={"mapnet": self._format_mapnet_response(mapnet_obj)})
    
    async def get_mapnets_by_ids(self, mapnet_ids: List[str], user: dict) -> Dict[str, Any]:
        """根据ID列表获取路网元素"""
        try:
            mapnets = await self.mapnet_repo.get_by_ids(mapnet_ids)
            
            items_data = [self._format_mapnet_response(mapnet) for mapnet in mapnets]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取路网元素列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取路网元素列表失败: {e}")
            raise
    
    async def get_mapnets_by_map(self, query: MapNetQuery, user: dict) -> Dict[str, Any]:
        """获取地图的路网元素列表"""
        try:
            # 地图存在性检查已完成，无需额外权限检查
            
            # 计算分页参数
            skip = (query.page - 1) * query.size
            
            # 查询数据
            mapnets, total = await self.mapnet_repo.get_by_map_id(
                map_id=query.map_id,
                map_net_type=query.map_net_type,
                skip=skip,
                limit=query.size
            )
            
            # 转换路网元素列表为字典列表
            mapnets_dict = [self._format_mapnet_response(mapnet_obj) for mapnet_obj in mapnets]
            
            return ApiResponse.paginated(
                items=mapnets_dict,
                total=total,
                page=query.page,
                size=query.size
            )
            
        except Exception as e:
            logger.error(
                "获取路网元素列表失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_id": query.map_id,
                    "map_net_type": query.map_net_type
                },
                exc_info=True
            )
            raise
    
    async def update_mapnet(self, mapnet_id: str, mapnet_data: MapNetUpdate, user: dict) -> Dict[str, Any]:
        """更新路网元素"""
        try:
            # 检查路网元素是否存在
            existing_mapnet = await self.mapnet_repo.get_by_id(mapnet_id)
            if not existing_mapnet:
                raise ResourceNotFoundError(f"路网元素 '{mapnet_id}' 不存在")
            
            # 路网元素存在性检查已完成，无需额外权限检查
            
            # 准备更新数据（只更新已设置的字段，包括0值）
            update_data = {}
            for field, value in mapnet_data.dict(exclude_unset=True).items():
                update_data[field] = value
            
            if update_data:
                update_data["updated_by"] = user["username"]
                
                # 更新路网元素
                mapnet_obj = await self.mapnet_repo.update(mapnet_id, update_data)
                
                # 记录业务日志
                log_user_action(
                    user=user["username"],
                    action="更新路网元素",
                    result="成功",
                    details=f"路网元素ID: {mapnet_id}, 更新字段: {list(update_data.keys())}"
                )
                
                logger.info(
                    "用户更新路网元素成功",
                    extra={
                        "user_id": user["id"],
                        "mapnet_id": mapnet_id,
                        "updated_fields": list(update_data.keys())
                    }
                )
                
                return ApiResponse.success(
                    data={"mapnet": self._format_mapnet_response(mapnet_obj)},
                    message="路网元素更新成功"
                )
            else:
                return ApiResponse.success(
                    data={"mapnet": self._format_mapnet_response(existing_mapnet)},
                    message="无需更新"
                )
                
        except Exception as e:
            logger.error(
                "更新路网元素失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "mapnet_id": mapnet_id
                },
                exc_info=True
            )
            raise
    
    async def delete_mapnet(self, mapnet_id: str, user: dict) -> Dict[str, Any]:
        """删除路网元素"""
        try:
            # 检查路网元素是否存在
            existing_mapnet = await self.mapnet_repo.get_by_id(mapnet_id)
            if not existing_mapnet:
                raise ResourceNotFoundError(f"路网元素 '{mapnet_id}' 不存在")
            
            # 路网元素存在性检查已完成，无需额外权限检查
            
            # 软删除路网元素
            success = await self.mapnet_repo.soft_delete(mapnet_id, user["username"])
            
            if success:
                # 记录业务日志
                log_user_action(
                    user=user["username"],
                    action="删除路网元素",
                    result="成功",
                    details=f"元素类型: {existing_mapnet.map_net_type}"
                )
                
                logger.info(
                    "用户删除路网元素成功",
                    extra={
                        "user_id": user["id"],
                        "mapnet_id": mapnet_id,
                        "map_net_type": existing_mapnet.map_net_type
                    }
                )
                
                return ApiResponse.success(message="路网元素删除成功")
            else:
                raise BusinessError("路网元素删除失败")
                
        except Exception as e:
            logger.error(
                "删除路网元素失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "mapnet_id": mapnet_id
                },
                exc_info=True
            )
            raise
    
    async def get_mapnet_stats(self, map_id: str, user: dict) -> Dict[str, Any]:
        """获取地图路网统计信息"""
        try:
            # 地图存在性检查已完成，无需额外权限检查
            
            # 获取统计信息
            total_count = await self.mapnet_repo.count_by_map_id(map_id)
            element_types = await self.mapnet_repo.get_types_by_map_id(map_id)
            
            return ApiResponse.success(
                data={
                    "map_id": map_id,
                    "total_elements": total_count,
                    "element_types": element_types,
                    "type_count": len(element_types)
                },
                message="获取路网统计成功"
            )
            
        except Exception as e:
            logger.error(
                "获取路网统计失败: %s",
                str(e),
                extra={
                    "user_id": user["id"],
                    "map_id": map_id
                },
                exc_info=True
            )
            raise
