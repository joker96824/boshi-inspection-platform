"""
巡检项目业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.item_repository import ItemRepository
from ..repositories.device_repository import DeviceRepository
from ..repositories.robot_repository import RobotRepository
from ..repositories.detectiontype_repository import DetectionTypeRepository
from ..schemas.item import ItemCreate, ItemUpdate, ItemQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class ItemService:
    """巡检项目业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.item_repo = ItemRepository(db)
        self.device_repo = DeviceRepository(db)
        self.robot_repo = RobotRepository(db)
        self.detection_type_repo = DetectionTypeRepository(db)
    
    async def create_item(self, item_data: ItemCreate, user: dict) -> Dict[str, Any]:
        """创建巡检项目"""
        try:
            # 检查设备是否存在
            device = await self.device_repo.get_by_id(item_data.device_id)
            if not device:
                raise ResourceNotFoundError(f"设备 '{item_data.device_id}' 不存在")
            
            # 如果提供了robot_id，检查机器人是否存在
            if item_data.robot_id:
                robot = await self.robot_repo.get_by_id(item_data.robot_id)
                if not robot:
                    raise ResourceNotFoundError(f"机器人 '{item_data.robot_id}' 不存在")
            
            # 如果提供了detection_type_id，检查检测类型是否存在
            if item_data.detection_type_id:
                detection_type = await self.detection_type_repo.get_by_id(item_data.detection_type_id)
                if not detection_type:
                    raise ResourceNotFoundError(f"检测类型 '{item_data.detection_type_id}' 不存在")
            
            # 检查巡检项目名是否已存在
            if await self.item_repo.exists_by_name(item_data.item_name):
                raise BusinessError(f"巡检项目名称 '{item_data.item_name}' 已存在")
            
            create_data = item_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            item = await self.item_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_item",
                "success",
                f"创建巡检项目成功，ID: {item.id}"
            )
            
            return ApiResponse.success(
                data=self._format_item_response(item),
                message="创建巡检项目成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建巡检项目失败: {e}")
            raise HTTPException(status_code=500, detail="创建巡检项目失败")
    
    async def get_item_by_id(self, item_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取巡检项目"""
        try:
            item = await self.item_repo.get_by_id(item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_item_response(item),
                message="获取巡检项目成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取巡检项目失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检项目失败")
    
    async def get_items_by_ids(self, item_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取巡检项目"""
        try:
            items = await self.item_repo.get_by_ids(item_ids)
            
            items_data = [self._format_item_response(item) for item in items]
            
            return ApiResponse.success(
                data={"items": items_data, "total": len(items_data)},
                message="获取巡检项目列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检项目列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检项目列表失败")
    
    async def get_items(self, query: ItemQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取巡检项目列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                items, total = await self.item_repo.get_all(
                    page=None,
                    size=None,
                    item_name=query.item_name,
                    device_id=query.device_id,
                    robot_id=query.robot_id
                )
                items_data = [self._format_item_response(item) for item in items]
                return ApiResponse.success(
                    data={"items": items_data, "total": total},
                    message="获取巡检项目列表成功"
                )
            
            items, total = await self.item_repo.get_all(
                page=query.page,
                size=query.size,
                item_name=query.item_name,
                device_id=query.device_id,
                robot_id=query.robot_id
            )
            
            # 格式化响应数据
            items_data = [self._format_item_response(item) for item in items]
            
            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检项目列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检项目列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检项目列表失败")
    
    async def update_item(self, item_id: str, item_data: ItemUpdate, user: dict) -> Dict[str, Any]:
        """更新巡检项目"""
        try:
            # 检查巡检项目是否存在
            existing_item = await self.item_repo.get_by_id(item_id)
            if not existing_item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            # 如果更新了device_id，检查设备是否存在
            if item_data.device_id and item_data.device_id != existing_item.device_id:
                device = await self.device_repo.get_by_id(item_data.device_id)
                if not device:
                    raise ResourceNotFoundError(f"设备 '{item_data.device_id}' 不存在")
            
            # 如果更新了robot_id，检查机器人是否存在
            if item_data.robot_id is not None and item_data.robot_id != existing_item.robot_id:
                if item_data.robot_id:  # 如果提供了非空值
                    robot = await self.robot_repo.get_by_id(item_data.robot_id)
                    if not robot:
                        raise ResourceNotFoundError(f"机器人 '{item_data.robot_id}' 不存在")
            
            # 如果更新了detection_type_id，检查检测类型是否存在
            if item_data.detection_type_id is not None and item_data.detection_type_id != existing_item.detection_type_id:
                if item_data.detection_type_id:  # 如果提供了非空值
                    detection_type = await self.detection_type_repo.get_by_id(item_data.detection_type_id)
                    if not detection_type:
                        raise ResourceNotFoundError(f"检测类型 '{item_data.detection_type_id}' 不存在")
            
            # 如果更新了名称，检查是否重复
            if (item_data.item_name and 
                item_data.item_name != existing_item.item_name and
                await self.item_repo.exists_by_name(item_data.item_name, item_id)):
                raise BusinessError(f"巡检项目名称 '{item_data.item_name}' 已存在")
            
            update_data = item_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_item = await self.item_repo.update(item_id, update_data)
            
            log_user_action(
                user["username"],
                "update_item",
                "success",
                f"更新巡检项目成功，ID: {item_id}"
            )
            
            return ApiResponse.success(
                data=self._format_item_response(updated_item),
                message="更新巡检项目成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新巡检项目失败: {e}")
            raise HTTPException(status_code=500, detail="更新巡检项目失败")
    
    async def delete_item(self, item_id: str, user: dict) -> Dict[str, Any]:
        """删除巡检项目"""
        try:
            # 检查巡检项目是否存在
            existing_item = await self.item_repo.get_by_id(item_id)
            if not existing_item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            # 删除巡检项目
            success = await self.item_repo.soft_delete(item_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_item",
                    "success",
                    f"删除巡检项目成功，ID: {item_id}"
                )
                
                return ApiResponse.success(
                    data={"id": item_id},
                    message="删除巡检项目成功"
                )
            else:
                raise HTTPException(status_code=500, detail="删除巡检项目失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除巡检项目失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除巡检项目失败: {e}")
            raise HTTPException(status_code=500, detail="删除巡检项目失败")
    
    async def get_item_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取巡检项目统计信息"""
        try:
            total_count = await self.item_repo.count_all()
            
            stats = {
                "total_items": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取巡检项目统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检项目统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检项目统计失败")
    
    def _format_item_response(self, item) -> Dict[str, Any]:
        """格式化巡检项目响应数据"""
        return {
            "id": item.id,
            "item_name": item.item_name,
            "item_info": item.item_info,
            "device_id": item.device_id,
            "robot_id": item.robot_id,
            "detection_type_id": item.detection_type_id,
            "enabled": item.enabled,
            "created_at": item.created_at.strftime("%Y-%m-%dT%H:%M:%S") if item.created_at else None,
            "updated_at": item.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if item.updated_at else None,
            "created_by": item.created_by,
            "updated_by": item.updated_by,
        }
