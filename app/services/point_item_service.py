"""
巡检中间表业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.point_item_repository import PointItemRepository
from ..repositories.point_repository import PointRepository
from ..repositories.item_repository import ItemRepository
from ..schemas.point_item import PointItemCreate, PointItemUpdate, PointItemQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class PointItemService:
    """巡检中间表业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.point_item_repo = PointItemRepository(db)
        self.point_repo = PointRepository(db)
        self.item_repo = ItemRepository(db)
    
    async def create_point_item(self, point_item_data: PointItemCreate, user: dict) -> Dict[str, Any]:
        """创建巡检中间表记录"""
        try:
            # 检查巡检点是否存在
            point = await self.point_repo.get_by_id(point_item_data.point_id)
            if not point:
                raise ResourceNotFoundError(f"巡检点ID '{point_item_data.point_id}' 不存在")
            
            # 检查巡检项目是否存在
            item = await self.item_repo.get_by_id(point_item_data.item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{point_item_data.item_id}' 不存在")
            
            # 检查关联是否已存在
            if await self.point_item_repo.exists_by_point_item(
                point_item_data.point_id, 
                point_item_data.item_id
            ):
                raise BusinessError(f"巡检点 '{point.point_name}' 和巡检项目 '{item.item_name}' 的关联已存在")
            
            create_data = point_item_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            point_item = await self.point_item_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_point_item",
                "success",
                f"创建巡检中间表记录成功，ID: {point_item.id}"
            )
            
            return ApiResponse.success(
                data=self._format_point_item_response(point_item),
                message="创建巡检中间表记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建巡检中间表记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建巡检中间表记录失败: {e}")
            raise HTTPException(status_code=500, detail="创建巡检中间表记录失败")
    
    async def get_point_item_by_id(self, point_item_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取巡检中间表记录"""
        try:
            point_item = await self.point_item_repo.get_by_id(point_item_id)
            if not point_item:
                raise ResourceNotFoundError(f"巡检中间表记录ID '{point_item_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_point_item_response(point_item),
                message="获取巡检中间表记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取巡检中间表记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取巡检中间表记录失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检中间表记录失败")
    
    async def get_point_items(self, query: PointItemQuery, user: dict) -> Dict[str, Any]:
        """获取巡检中间表记录列表"""
        try:
            point_items, total = await self.point_item_repo.get_all(
                page=query.page,
                size=query.size,
                point_ids=query.point_ids,
                item_ids=query.item_ids
            )
            
            # 格式化响应数据
            items_data = [self._format_point_item_response(point_item) for point_item in point_items]
            
            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检中间表记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检中间表记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检中间表记录列表失败")
    
    async def get_point_items_with_item_details(self, query: PointItemQuery, user: dict) -> Dict[str, Any]:
        """通过巡检点查询，返回带巡检项目详情的记录列表"""
        try:
            point_items_with_details, total = await self.point_item_repo.get_with_item_details(
                page=query.page,
                size=query.size,
                point_ids=query.point_ids
            )
            
            # 格式化时间字段
            for item in point_items_with_details:
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
                if item.get("updated_at"):
                    item["updated_at"] = item["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
            
            return ApiResponse.paginated(
                items=point_items_with_details,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检中间表记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检中间表记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检中间表记录列表失败")
    
    async def get_point_items_with_point_details(self, query: PointItemQuery, user: dict) -> Dict[str, Any]:
        """通过巡检项目查询，返回带巡检点详情的记录列表"""
        try:
            point_items_with_details, total = await self.point_item_repo.get_with_point_details(
                page=query.page,
                size=query.size,
                item_ids=query.item_ids
            )
            
            # 格式化时间字段
            for item in point_items_with_details:
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
                if item.get("updated_at"):
                    item["updated_at"] = item["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
            
            return ApiResponse.paginated(
                items=point_items_with_details,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检中间表记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检中间表记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检中间表记录列表失败")
    
    async def update_point_item(self, point_item_id: str, point_item_data: PointItemUpdate, user: dict) -> Dict[str, Any]:
        """更新巡检中间表记录"""
        try:
            # 检查记录是否存在
            existing_point_item = await self.point_item_repo.get_by_id(point_item_id)
            if not existing_point_item:
                raise ResourceNotFoundError(f"巡检中间表记录ID '{point_item_id}' 不存在")
            
            # 如果更新了巡检点，检查是否存在
            if point_item_data.point_id:
                point = await self.point_repo.get_by_id(point_item_data.point_id)
                if not point:
                    raise ResourceNotFoundError(f"巡检点ID '{point_item_data.point_id}' 不存在")
            
            # 如果更新了巡检项目，检查是否存在
            if point_item_data.item_id:
                item = await self.item_repo.get_by_id(point_item_data.item_id)
                if not item:
                    raise ResourceNotFoundError(f"巡检项目ID '{point_item_data.item_id}' 不存在")
            
            # 如果同时更新了巡检点和巡检项目，检查新关联是否已存在
            if point_item_data.point_id and point_item_data.item_id:
                if await self.point_item_repo.exists_by_point_item(
                    point_item_data.point_id, 
                    point_item_data.item_id, 
                    point_item_id
                ):
                    raise BusinessError("巡检点和巡检项目的关联已存在")
            
            update_data = point_item_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_point_item = await self.point_item_repo.update(point_item_id, update_data)
            
            log_user_action(
                user["username"],
                "update_point_item",
                "success",
                f"更新巡检中间表记录成功，ID: {point_item_id}"
            )
            
            return ApiResponse.success(
                data=self._format_point_item_response(updated_point_item),
                message="更新巡检中间表记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新巡检中间表记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新巡检中间表记录失败: {e}")
            raise HTTPException(status_code=500, detail="更新巡检中间表记录失败")
    
    async def delete_point_item(self, point_item_id: str, user: dict) -> Dict[str, Any]:
        """删除巡检中间表记录（真删除）"""
        try:
            # 检查记录是否存在
            existing_point_item = await self.point_item_repo.get_by_id(point_item_id)
            if not existing_point_item:
                raise ResourceNotFoundError(f"巡检中间表记录ID '{point_item_id}' 不存在")
            
            success = await self.point_item_repo.delete(point_item_id)
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_point_item",
                    "success",
                    f"删除巡检中间表记录成功，ID: {point_item_id}"
                )
                
                return ApiResponse.success(message="删除巡检中间表记录成功")
            else:
                raise HTTPException(status_code=500, detail="删除巡检中间表记录失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除巡检中间表记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除巡检中间表记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除巡检中间表记录失败")

    async def update_point_item_by_item(self, item_id: str, point_ids: List[str], user: dict) -> Dict[str, Any]:
        """通过巡检项目ID批量更新关联关系"""
        try:
            # 验证巡检项目是否存在
            item = await self.item_repo.get_by_id(item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            # 验证所有巡检点是否存在
            for point_id in point_ids:
                point = await self.point_repo.get_by_id(point_id)
                if not point:
                    raise ResourceNotFoundError(f"巡检点ID '{point_id}' 不存在")
            
            # 删除该巡检项目的所有现有关联
            deleted_count = await self.point_item_repo.delete_by_item_id(item_id)
            
            # 创建新的关联关系
            created_point_items = []
            if point_ids:
                created_point_items = await self.point_item_repo.batch_create_by_item(item_id, point_ids, user)
            
            log_user_action(
                user["username"],
                "update_point_item_by_item",
                "success",
                f"批量更新巡检项目关联关系成功，项目ID: {item_id}，删除: {deleted_count}，创建: {len(created_point_items)}"
            )
            
            return ApiResponse.success(
                data={
                    "item_id": item_id,
                    "deleted_count": deleted_count,
                    "created_count": len(created_point_items),
                    "point_ids": point_ids
                },
                message="批量更新巡检项目关联关系成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"批量更新巡检项目关联关系失败: {e}")
            raise
        except Exception as e:
            logger.error(f"批量更新巡检项目关联关系失败: {e}")
            raise HTTPException(status_code=500, detail="批量更新巡检项目关联关系失败")

    async def update_point_item_by_point(self, point_id: str, item_ids: List[str], user: dict) -> Dict[str, Any]:
        """通过巡检点ID批量更新关联关系"""
        try:
            # 验证巡检点是否存在
            point = await self.point_repo.get_by_id(point_id)
            if not point:
                raise ResourceNotFoundError(f"巡检点ID '{point_id}' 不存在")
            
            # 验证所有巡检项目是否存在
            for item_id in item_ids:
                item = await self.item_repo.get_by_id(item_id)
                if not item:
                    raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            # 删除该巡检点的所有现有关联
            deleted_count = await self.point_item_repo.delete_by_point_id(point_id)
            
            # 创建新的关联关系
            created_point_items = []
            if item_ids:
                created_point_items = await self.point_item_repo.batch_create_by_point(point_id, item_ids, user)
            
            log_user_action(
                user["username"],
                "update_point_item_by_point",
                "success",
                f"批量更新巡检点关联关系成功，点ID: {point_id}，删除: {deleted_count}，创建: {len(created_point_items)}"
            )
            
            return ApiResponse.success(
                data={
                    "point_id": point_id,
                    "deleted_count": deleted_count,
                    "created_count": len(created_point_items),
                    "item_ids": item_ids
                },
                message="批量更新巡检点关联关系成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"批量更新巡检点关联关系失败: {e}")
            raise
        except Exception as e:
            logger.error(f"批量更新巡检点关联关系失败: {e}")
            raise HTTPException(status_code=500, detail="批量更新巡检点关联关系失败")

    async def delete_point_items_by_item(self, item_id: str, user: dict) -> Dict[str, Any]:
        """删除指定巡检项目的所有关联记录（真删除）"""
        try:
            # 验证巡检项目是否存在
            item = await self.item_repo.get_by_id(item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{item_id}' 不存在")
            
            # 删除该巡检项目的所有关联记录
            deleted_count = await self.point_item_repo.delete_by_item_id(item_id)
            
            log_user_action(
                user["username"],
                "delete_point_items_by_item",
                "success",
                f"删除巡检项目所有关联记录成功，项目ID: {item_id}，删除数量: {deleted_count}"
            )
            
            return ApiResponse.success(
                data={
                    "item_id": item_id,
                    "deleted_count": deleted_count
                },
                message="删除巡检项目所有关联记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除巡检项目关联记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除巡检项目关联记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除巡检项目关联记录失败")

    async def delete_point_items_by_point(self, point_id: str, user: dict) -> Dict[str, Any]:
        """删除指定巡检点的所有关联记录（真删除）"""
        try:
            # 验证巡检点是否存在
            point = await self.point_repo.get_by_id(point_id)
            if not point:
                raise ResourceNotFoundError(f"巡检点ID '{point_id}' 不存在")
            
            # 删除该巡检点的所有关联记录
            deleted_count = await self.point_item_repo.delete_by_point_id(point_id)
            
            log_user_action(
                user["username"],
                "delete_point_items_by_point",
                "success",
                f"删除巡检点所有关联记录成功，点ID: {point_id}，删除数量: {deleted_count}"
            )
            
            return ApiResponse.success(
                data={
                    "point_id": point_id,
                    "deleted_count": deleted_count
                },
                message="删除巡检点所有关联记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除巡检点关联记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除巡检点关联记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除巡检点关联记录失败")
    
    async def get_point_item_stats(self, user: dict) -> Dict[str, Any]:
        """获取巡检中间表统计信息"""
        try:
            # 这里可以添加更多统计信息
            stats = {
                "message": "统计功能待实现"
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取巡检中间表统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检中间表统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检中间表统计失败")
    
    def _format_point_item_response(self, point_item) -> Dict[str, Any]:
        """格式化巡检中间表响应数据"""
        return {
            "id": point_item.id,
            "point_id": point_item.point_id,
            "item_id": point_item.item_id,
            "created_at": point_item.created_at.strftime("%Y-%m-%dT%H:%M:%S") if point_item.created_at else None,
            "updated_at": point_item.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if point_item.updated_at else None,
            "created_by": point_item.created_by,
            "updated_by": point_item.updated_by,
        }
