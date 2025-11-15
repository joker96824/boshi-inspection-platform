"""
厂区业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.factory_repository import FactoryRepository
from ..schemas.factory import FactoryCreate, FactoryUpdate, FactoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action
import uuid
from datetime import datetime

logger = get_logger(__name__)


class FactoryService:
    """厂区业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.factory_repo = FactoryRepository(db)
    
    def _format_factory_response(self, factory) -> dict:
        """格式化厂区响应数据"""
        return {
            "id": factory.id,
            "factory_name": factory.factory_name,
            "created_at": factory.created_at,
            "updated_at": factory.updated_at,
            "created_by": factory.created_by,
            "updated_by": factory.updated_by
        }
    
    async def create_factory(self, factory_data: FactoryCreate, user: dict) -> Dict[str, Any]:
        """创建厂区"""
        try:
            # 检查厂区名是否已存在
            if await self.factory_repo.exists_by_name(factory_data.factory_name):
                raise BusinessError(f"厂区名称 '{factory_data.factory_name}' 已存在")
            
            # 准备创建数据
            create_data = {
                "id": str(uuid.uuid4()),
                "factory_name": factory_data.factory_name,
                "created_by": user.get("username"),
                "updated_by": user.get("username")
            }
            
            # 创建厂区
            factory = await self.factory_repo.create(create_data)
            
            # 记录日志
            log_user_action(logger, user, "create_factory", f"创建厂区: {factory.factory_name}")
            
            return ApiResponse.success(
                data=self._format_factory_response(factory),
                message="厂区创建成功"
            )
        except BusinessError:
            raise
        except Exception as e:
            logger.error(f"创建厂区失败: {e}", exc_info=True)
            raise BusinessError(f"创建厂区失败: {str(e)}")
    
    async def get_factory(self, factory_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """获取厂区详情"""
        try:
            factory = await self.factory_repo.get_by_id(factory_id)
            
            if not factory:
                raise ResourceNotFoundError(f"厂区 '{factory_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_factory_response(factory),
                message="获取厂区成功"
            )
        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取厂区失败: {e}", exc_info=True)
            raise BusinessError(f"获取厂区失败: {str(e)}")
    
    async def list_factories(self, query: FactoryQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取厂区列表"""
        try:
            # 如果未提供分页参数，返回所有数据
            if query.page is None or query.size is None:
                factories, total = await self.factory_repo.get_all(
                    page=None,
                    size=None,
                    factory_name=query.factory_name
                )
                items = [self._format_factory_response(f) for f in factories]
                return ApiResponse.success(
                    data={"items": items, "total": total},
                    message="获取厂区列表成功"
                )
            
            factories, total = await self.factory_repo.get_all(
                page=query.page,
                size=query.size,
                factory_name=query.factory_name
            )
            
            items = [self._format_factory_response(f) for f in factories]
            
            return ApiResponse.paginated(
                items=items,
                total=total,
                page=query.page,
                size=query.size
            )
        except Exception as e:
            logger.error(f"获取厂区列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取厂区列表失败: {str(e)}")
    
    async def update_factory(self, factory_id: str, factory_data: FactoryUpdate, user: dict) -> Dict[str, Any]:
        """更新厂区"""
        try:
            # 检查厂区是否存在
            factory = await self.factory_repo.get_by_id(factory_id)
            if not factory:
                raise ResourceNotFoundError(f"厂区 '{factory_id}' 不存在")
            
            # 准备更新数据
            update_data = factory_data.dict(exclude_unset=True)
            
            # 如果有厂区名，检查是否重复
            if "factory_name" in update_data:
                if await self.factory_repo.exists_by_name(update_data["factory_name"], exclude_id=factory_id):
                    raise BusinessError(f"厂区名称 '{update_data['factory_name']}' 已存在")
            
            update_data["updated_by"] = user.get("username")
            
            # 更新厂区
            updated_factory = await self.factory_repo.update(factory_id, update_data)
            
            if not updated_factory:
                raise ResourceNotFoundError(f"厂区 '{factory_id}' 不存在")
            
            # 记录日志
            log_user_action(logger, user, "update_factory", f"更新厂区: {factory_id}")
            
            return ApiResponse.success(
                data=self._format_factory_response(updated_factory),
                message="厂区更新成功"
            )
        except (ResourceNotFoundError, BusinessError):
            raise
        except Exception as e:
            logger.error(f"更新厂区失败: {e}", exc_info=True)
            raise BusinessError(f"更新厂区失败: {str(e)}")
    
    async def delete_factory(self, factory_id: str, user: dict) -> Dict[str, Any]:
        """删除厂区"""
        try:
            # 检查厂区是否存在
            factory = await self.factory_repo.get_by_id(factory_id)
            if not factory:
                raise ResourceNotFoundError(f"厂区 '{factory_id}' 不存在")
            
            # 软删除厂区
            success = await self.factory_repo.soft_delete(factory_id, user.get("username"))
            
            if not success:
                raise BusinessError("软删除操作返回失败")
            
            # 记录日志
            log_user_action(logger, user, "delete_factory", f"删除厂区: {factory.factory_name}")
            
            return ApiResponse.success(
                data={"id": factory_id},
                message="厂区删除成功"
            )
        except (ResourceNotFoundError, BusinessError):
            raise
        except Exception as e:
            logger.error(f"删除厂区失败: {e}", exc_info=True)
            raise BusinessError(f"删除厂区失败: {str(e)}")
    
    async def get_factories_by_ids(self, factory_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取厂区"""
        try:
            factories = await self.factory_repo.get_by_ids(factory_ids)
            
            items = [self._format_factory_response(f) for f in factories]
            
            return ApiResponse.success(
                data={"factories": items},
                message="获取厂区成功"
            )
        except Exception as e:
            logger.error(f"获取厂区列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取厂区列表失败: {str(e)}")

