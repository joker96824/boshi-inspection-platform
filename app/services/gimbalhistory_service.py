"""
云台记录业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from ..repositories.gimbalhistory_repository import GimbalHistoryRepository
from ..repositories.gimbaltask_repository import GimbalTaskRepository
from ..schemas.gimbalhistory import GimbalHistoryCreate, GimbalHistoryUpdate, GimbalHistoryQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class GimbalHistoryService:
    """云台记录业务逻辑服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.gimbal_history_repo = GimbalHistoryRepository(db)
        self.gimbal_task_repo = GimbalTaskRepository(db)
    
    async def create_gimbal_history(self, history_data: GimbalHistoryCreate, user: dict) -> Dict[str, Any]:
        """创建云台记录"""
        try:
            # 检查云台任务是否存在
            gimbal_task = await self.gimbal_task_repo.get_by_id(history_data.gimbaltask_id)
            if not gimbal_task:
                raise ResourceNotFoundError(f"云台任务ID '{history_data.gimbaltask_id}' 不存在")
            
            create_data = history_data.dict()
            create_data["created_by"] = user["username"]
            create_data["updated_by"] = user["username"]
            
            history = await self.gimbal_history_repo.create(create_data)
            
            log_user_action(
                user["username"],
                "create_gimbal_history",
                "success",
                f"创建云台记录成功，ID: {history.id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_history_response(history),
                message="创建云台记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"创建云台记录失败: {e}")
            raise
        except IntegrityError as e:
            error_msg = str(e.orig) if hasattr(e, 'orig') else str(e)
            if "foreign key constraint" in error_msg.lower() or "1452" in error_msg:
                logger.error(f"创建云台记录失败-外键约束错误: {error_msg}")
                raise BusinessError("关联的云台任务不存在，请检查云台任务ID是否正确")
            else:
                logger.error(f"创建云台记录失败-数据库完整性错误: {error_msg}")
                raise BusinessError(f"数据完整性验证失败")
        except Exception as e:
            logger.error(f"创建云台记录失败: {e}", exc_info=True)
            raise BusinessError(f"创建云台记录失败: {str(e)}")
    
    async def get_gimbal_history_by_id(self, history_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取云台记录"""
        try:
            history = await self.gimbal_history_repo.get_by_id(history_id)
            if not history:
                raise ResourceNotFoundError(f"云台记录ID '{history_id}' 不存在")
            
            return ApiResponse.success(
                data=self._format_gimbal_history_response(history),
                message="获取云台记录成功"
            )
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"获取云台记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"获取云台记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台记录失败: {str(e)}")
    
    async def get_gimbal_histories_by_ids(self, gimbalhistory_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取云台记录"""
        try:
            histories = await self.gimbal_history_repo.get_by_ids(gimbalhistory_ids)
            
            histories_data = [self._format_gimbal_history_response(history) for history in histories]
            
            return ApiResponse.success(
                data={"gimbal_histories": histories_data, "total": len(histories_data)},
                message="获取云台记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台记录列表失败: {str(e)}")
    
    async def get_gimbal_histories(self, query: GimbalHistoryQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台记录列表"""
        try:
            histories, total = await self.gimbal_history_repo.get_all(
                page=query.page,
                size=query.size,
                gimbaltask_id=query.gimbaltask_id
            )
            
            # 格式化响应数据
            histories_data = [self._format_gimbal_history_response(history) for history in histories]
            
            return ApiResponse.paginated(
                items=histories_data,
                total=total,
                page=query.page,
                size=query.size,
                message="获取云台记录列表成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台记录列表失败: {str(e)}")
    
    async def update_gimbal_history(self, history_id: str, history_data: GimbalHistoryUpdate, user: dict) -> Dict[str, Any]:
        """更新云台记录"""
        try:
            # 检查云台记录是否存在
            existing_history = await self.gimbal_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"云台记录ID '{history_id}' 不存在")
            
            # 如果更新了云台任务ID，检查云台任务是否存在
            if history_data.gimbaltask_id and history_data.gimbaltask_id != existing_history.gimbaltask_id:
                gimbal_task = await self.gimbal_task_repo.get_by_id(history_data.gimbaltask_id)
                if not gimbal_task:
                    raise ResourceNotFoundError(f"云台任务ID '{history_data.gimbaltask_id}' 不存在")
            
            update_data = history_data.dict(exclude_unset=True)
            update_data["updated_by"] = user["username"]
            
            updated_history = await self.gimbal_history_repo.update(history_id, update_data)
            
            log_user_action(
                user["username"],
                "update_gimbal_history",
                "success",
                f"更新云台记录成功，ID: {history_id}"
            )
            
            return ApiResponse.success(
                data=self._format_gimbal_history_response(updated_history),
                message="更新云台记录成功"
            )
            
        except (ResourceNotFoundError, BusinessError) as e:
            logger.warning(f"更新云台记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"更新云台记录失败: {e}", exc_info=True)
            raise BusinessError(f"更新云台记录失败: {str(e)}")
    
    async def delete_gimbal_history(self, history_id: str, user: dict) -> Dict[str, Any]:
        """删除云台记录"""
        try:
            # 检查云台记录是否存在
            existing_history = await self.gimbal_history_repo.get_by_id(history_id)
            if not existing_history:
                raise ResourceNotFoundError(f"云台记录ID '{history_id}' 不存在")
            
            # 删除云台记录
            success = await self.gimbal_history_repo.soft_delete(history_id, user["username"])
            
            if success:
                log_user_action(
                    user["username"],
                    "delete_gimbal_history",
                    "success",
                    f"删除云台记录成功，ID: {history_id}"
                )
                
                return ApiResponse.success(
                    data={"history_id": history_id},
                    message="删除云台记录成功"
                )
            else:
                raise BusinessError("删除云台记录失败")
            
        except (ResourceNotFoundError) as e:
            logger.warning(f"删除云台记录失败: {e}")
            raise
        except Exception as e:
            logger.error(f"删除云台记录失败: {e}", exc_info=True)
            raise BusinessError(f"删除云台记录失败: {str(e)}")
    
    async def get_gimbal_history_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取云台记录统计信息"""
        try:
            total_count = await self.gimbal_history_repo.count_all()
            
            stats = {
                "total_histories": total_count
            }
            
            return ApiResponse.success(
                data=stats,
                message="获取云台记录统计成功"
            )
            
        except Exception as e:
            logger.error(f"获取云台记录统计失败: {e}", exc_info=True)
            raise BusinessError(f"获取云台记录统计失败: {str(e)}")
    
    def _format_gimbal_history_response(self, history) -> Dict[str, Any]:
        """格式化云台记录响应数据"""
        return {
            "id": history.id,
            "gimbaltask_id": history.gimbaltask_id,
            "record_data": history.record_data,
            "media_url": history.media_url,
            "created_at": history.created_at.strftime("%Y-%m-%dT%H:%M:%S") if history.created_at else None,
            "updated_at": history.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if history.updated_at else None,
            "created_by": history.created_by,
            "updated_by": history.updated_by,
        }
