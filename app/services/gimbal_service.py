"""
云台业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from ..repositories.gimbal_repository import GimbalRepository
from ..schemas.gimbal import GimbalCreate, GimbalUpdate, GimbalQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalService:
    """云台业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_repo = GimbalRepository(db)
    
    async def create_gimbal(self, gimbal_data: GimbalCreate, user: dict) -> Dict[str, Any]:
        """创建云台"""
        try:
            # 检查云台名是否已存在
            if await self.gimbal_repo.exists_by_name(gimbal_data.gimbal_name):
                raise BusinessError(f"云台名称 '{gimbal_data.gimbal_name}' 已存在")
            
            create_data = gimbal_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            gimbal = await self.gimbal_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_gimbal",
                "success",
                f"创建云台成功，ID: {gimbal.id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_response(gimbal),
                message="创建云台成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"创建云台失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台失败: {str(e)}")
    
    async def get_gimbal_by_id(self, gimbal_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取云台"""
        try:
            gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_gimbal_response(gimbal),
                message="获取云台成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台失败: {str(e)}")
    
    async def get_gimbals_by_ids(self, gimbal_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取云台"""
        try:
            gimbals = await self.gimbal_repo.get_by_ids(gimbal_ids)
            
            gimbals_data = [self._format_gimbal_response(gimbal) for gimbal in gimbals]
            
            return ApiResponse.success(
                data={"gimbals": gimbals_data, "total": len(gimbals_data)},
                message="获取云台列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台列表失败: {str(e)}")
    
    async def get_gimbals(self, query: GimbalQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台列表"""
        try:
            gimbals, total = await self.gimbal_repo.get_all(
                page=query.page,
                size=query.size,
                gimbal_name=query.gimbal_name,
                map_id=query.map_id
            )
            
            # 格式化响应数据
            gimbals_data = [self._format_gimbal_response(gimbal) for gimbal in gimbals]
            
            return ApiResponse.paginated(
                items=gimbals_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台列表失败: {str(e)}")
    
    async def update_gimbal(self, gimbal_id: str, gimbal_data: GimbalUpdate, user: dict) -> Dict[str, Any]:
        """更新云台"""
        try:
            # 检查云台是否存在
            existing_gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not existing_gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            # 如果更新了名称，检查是否重复
            if (gimbal_data.gimbal_name and 
                gimbal_data.gimbal_name != existing_gimbal.gimbal_name and
                await self.gimbal_repo.exists_by_name(gimbal_data.gimbal_name, gimbal_id)):
                raise BusinessError(f"云台名称 '{gimbal_data.gimbal_name}' 已存在")
            
            update_data = gimbal_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_gimbal = await self.gimbal_repo.update(gimbal_id, update_data)
            
            log_user_action(
                user["username"],
                "update_gimbal",
                "success",
                f"更新云台成功，ID: {gimbal_id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_response(updated_gimbal),
                message="更新云台成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台失败: {str(e)}")
    
    async def delete_gimbal(self, gimbal_id: str, user: dict) -> Dict[str, Any]:
        """删除云台"""
        try:
            # 检查云台是否存在
            existing_gimbal = await self.gimbal_repo.get_by_id(gimbal_id)
            if not existing_gimbal:
                raise ResourceNotFoundError(f"云台ID '{gimbal_id}' 不存在")
            
            # 删除云台
            success = await self.gimbal_repo.soft_delete(gimbal_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal",
                    "success",
                    f"删除云台成功，ID: {gimbal_id}"
                )
                
                return ApiResponse.success(
                    data={"id": gimbal_id},
                    message="删除云台成功"
                )
            else:
                raise BusinessError("删除云台失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除云台失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台失败: {str(e)}")
    
    async def get_gimbal_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台统计信息"""
        try:
            total_count = await self.gimbal_repo.count_all()
            
            stats = {
                "total_gimbals": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取云台统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台统计失败: {str(e)}")
    
    def _format_gimbal_response(self, gimbal) -> Dict[str, Any]:
        """格式化云台响应数据"""
        return {
            "id": gimbal.id,
            "gimbal_name": gimbal.gimbal_name,
            "gimbal_params": gimbal.gimbal_params,
            "map_id": gimbal.map_id,
            "created_at": gimbal.created_at.strftime("%Y-%m-%dT%H:%M:%S") if gimbal.created_at else None,
            "updated_at": gimbal.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if gimbal.updated_at else None,
            "created_by": gimbal.created_by,
            "updated_by": gimbal.updated_by,
        }

