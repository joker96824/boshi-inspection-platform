"""
巡检记录业务逻辑服务
"""

from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.itemhistory_repository import ItemHistoryRepository
from ..repositories.taskhistory_repository import TaskHistoryRepository
from ..repositories.item_repository import ItemRepository
from ..schemas.itemhistory import ItemHistoryCreate, ItemHistoryUpdate, ItemHistoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class ItemHistoryService:
    """巡检记录业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.itemhistory_repo = ItemHistoryRepository(db)
        self.taskhistory_repo = TaskHistoryRepository(db)
        self.item_repo = ItemRepository(db)
    
    async def create_itemhistory(self, itemhistory_data: ItemHistoryCreate, user: dict) -> Dict[str, Any]:
        """创建巡检记录"""
        try:
            # 检查任务记录是否存在
            taskhistory = await self.taskhistory_repo.get_by_id(itemhistory_data.taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{itemhistory_data.taskhistory_id}' 不存在")
            
            # 检查巡检项目是否存在
            item = await self.item_repo.get_by_id(itemhistory_data.item_id)
            if not item:
                raise ResourceNotFoundError(f"巡检项目ID '{itemhistory_data.item_id}' 不存在")
            
            # 检查关联是否已存在
            if await self.itemhistory_repo.exists_by_taskhistory_item(
                itemhistory_data.taskhistory_id, 
                itemhistory_data.item_id
            ):
                raise BusinessError(f"任务记录和巡检项目的关联已存在")
            
            create_data = itemhistory_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            itemhistory = await self.itemhistory_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_itemhistory",
                "success",
                f"创建巡检记录成功，ID: {itemhistory.id}"
            )
            
            return ApiResponse.success(
                data=self._format_itemhistory_response(itemhistory),
                message="创建巡检记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建巡检记录失败: {e}")
            raise HTTPException(status_code=500, detail="创建巡检记录失败")
    
    async def get_itemhistory_by_id(self, itemhistory_id: str, user: dict) -> Dict[str, Any]:
        """根据ID获取巡检记录"""
        try:
            itemhistory = await self.itemhistory_repo.get_by_id(itemhistory_id)
            if not itemhistory:
                raise ResourceNotFoundError(f"巡检记录ID '{itemhistory_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_itemhistory_response(itemhistory),
                message="获取巡检记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取巡检记录失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检记录失败")
    
    async def get_itemhistories(self, query: ItemHistoryQuery, user: dict) -> Dict[str, Any]:
        """获取巡检记录列表"""
        try:
            itemhistories, total = await self.itemhistory_repo.get_all(
                page=query.page,
                size=query.size,
                taskhistory_id=query.taskhistory_id,
                item_id=query.item_id,
                taskhistory_ids=query.taskhistory_ids,
                item_ids=query.item_ids
            )
            
            # 格式化响应数据
            items_data = [self._format_itemhistory_response(itemhistory) for itemhistory in itemhistories]
            
            return ApiResponse.paginated(
                items=items_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检记录列表失败")
    
    async def get_itemhistories_with_taskhistory_details(self, query: ItemHistoryQuery, user: dict) -> Dict[str, Any]:
        """通过任务记录查询，返回带巡检项目详情的记录列表"""
        try:
            itemhistories_with_details, total = await self.itemhistory_repo.get_with_taskhistory_details(
                page=query.page,
                size=query.size,
                taskhistory_ids=query.taskhistory_ids
            )
            
            # 格式化时间字段
            for item in itemhistories_with_details:
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
                if item.get("updated_at"):
                    item["updated_at"] = item["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
            
            return ApiResponse.paginated(
                items=itemhistories_with_details,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检记录列表失败")

    async def get_itemhistories_with_item_details(self, query: ItemHistoryQuery, user: dict) -> Dict[str, Any]:
        """通过巡检项目查询，返回带任务记录详情的记录列表"""
        try:
            itemhistories_with_details, total = await self.itemhistory_repo.get_with_item_details(
                page=query.page,
                size=query.size,
                item_ids=query.item_ids
            )
            
            # 格式化时间字段
            for item in itemhistories_with_details:
                if item.get("created_at"):
                    item["created_at"] = item["created_at"].strftime("%Y-%m-%dT%H:%M:%S")
                if item.get("updated_at"):
                    item["updated_at"] = item["updated_at"].strftime("%Y-%m-%dT%H:%M:%S")
            
            return ApiResponse.paginated(
                items=itemhistories_with_details,
                total=total,
                page=query.page,
                size=query.size,
                message="获取巡检记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检记录列表失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检记录列表失败")
    
    async def update_itemhistory(self, itemhistory_id: str, itemhistory_data: ItemHistoryUpdate, user: dict) -> Dict[str, Any]:
        """更新巡检记录"""
        try:
            # 检查记录是否存在
            existing_itemhistory = await self.itemhistory_repo.get_by_id(itemhistory_id)
            if not existing_itemhistory:
                raise ResourceNotFoundError(f"巡检记录ID '{itemhistory_id}' 不存在")
            
            # 如果更新了任务记录，检查是否存在
            if itemhistory_data.taskhistory_id:
                taskhistory = await self.taskhistory_repo.get_by_id(itemhistory_data.taskhistory_id)
                if not taskhistory:
                    raise ResourceNotFoundError(f"任务记录ID '{itemhistory_data.taskhistory_id}' 不存在")
            
            # 如果更新了巡检项目，检查是否存在
            if itemhistory_data.item_id:
                item = await self.item_repo.get_by_id(itemhistory_data.item_id)
                if not item:
                    raise ResourceNotFoundError(f"巡检项目ID '{itemhistory_data.item_id}' 不存在")
            
            # 如果同时更新了任务记录和巡检项目，检查新关联是否已存在
            if itemhistory_data.taskhistory_id and itemhistory_data.item_id:
                if await self.itemhistory_repo.exists_by_taskhistory_item(
                    itemhistory_data.taskhistory_id, 
                    itemhistory_data.item_id, 
                    itemhistory_id
                ):
                    raise BusinessError("任务记录和巡检项目的关联已存在")
            
            update_data = itemhistory_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_itemhistory = await self.itemhistory_repo.update(itemhistory_id, update_data)
            
            log_user_action(
                user["username"],
                "update_itemhistory",
                "success",
                f"更新巡检记录成功，ID: {itemhistory_id}"
            )
            
            return ApiResponse.success(
                data=self._format_itemhistory_response(updated_itemhistory),
                message="更新巡检记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新巡检记录失败: {e}")
            raise HTTPException(status_code=500, detail="更新巡检记录失败")
    
    async def delete_itemhistory(self, itemhistory_id: str, user: dict) -> Dict[str, Any]:
        """删除巡检记录（真删除）"""
        try:
            # 检查记录是否存在
            existing_itemhistory = await self.itemhistory_repo.get_by_id(itemhistory_id)
            if not existing_itemhistory:
                raise ResourceNotFoundError(f"巡检记录ID '{itemhistory_id}' 不存在")
            
            success = await self.itemhistory_repo.delete(itemhistory_id)
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_itemhistory",
                    "success",
                    f"删除巡检记录成功，ID: {itemhistory_id}"
                )
                
                return ApiResponse.success(message="删除巡检记录成功")
            else:
                raise HTTPException(status_code=500, detail="删除巡检记录失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除巡检记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除巡检记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除巡检记录失败")

    async def delete_itemhistories_by_taskhistory(self, taskhistory_id: str, user: dict) -> Dict[str, Any]:
        """删除指定任务记录的所有关联记录（真删除）"""
        try:
            # 验证任务记录是否存在
            taskhistory = await self.taskhistory_repo.get_by_id(taskhistory_id)
            if not taskhistory:
                raise ResourceNotFoundError(f"任务记录ID '{taskhistory_id}' 不存在")
            
            # 删除该任务记录的所有关联记录
            deleted_count = await self.itemhistory_repo.delete_by_taskhistory_id(taskhistory_id)
            
            log_user_action(
                user["username"],
                "delete_itemhistories_by_taskhistory",
                "success",
                f"删除任务记录所有关联记录成功，任务记录ID: {taskhistory_id}，删除数量: {deleted_count}"
            )
            
            return ApiResponse.success(
                data={
                    "taskhistory_id": taskhistory_id,
                    "deleted_count": deleted_count
                },
                message="删除任务记录所有关联记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除任务记录关联记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除任务记录关联记录失败: {e}")
            raise HTTPException(status_code=500, detail="删除任务记录关联记录失败")

    async def get_itemhistory_stats(self, user: dict) -> Dict[str, Any]:
        """获取巡检记录统计信息"""
        try:
            total_count = await self.itemhistory_repo.count_all()
            
            stats = {
                "total_itemhistories": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取巡检记录统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取巡检记录统计失败: {e}")
            raise HTTPException(status_code=500, detail="获取巡检记录统计失败")
    
    def _format_itemhistory_response(self, itemhistory) -> Dict[str, Any]:
        """格式化巡检记录响应数据"""
        return {
            "id": itemhistory.id,
            "taskhistory_id": itemhistory.taskhistory_id,
            "item_id": itemhistory.item_id,
            "item_result": itemhistory.item_result,
            "created_at": itemhistory.created_at.strftime("%Y-%m-%dT%H:%M:%S") if itemhistory.created_at else None,
            "updated_at": itemhistory.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if itemhistory.updated_at else None,
            "created_by": itemhistory.created_by,
            "updated_by": itemhistory.updated_by,
        }
