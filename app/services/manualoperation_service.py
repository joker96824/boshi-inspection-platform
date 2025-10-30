"""
手动操作记录业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime

from ..repositories.manualoperation_repository import ManualOperationRepository
from ..schemas.manualoperation import ManualOperationCreate, ManualOperationUpdate, ManualOperationQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class ManualOperationService:
    """手动操作记录业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ManualOperationRepository(db)

    async def create_manual_operation(self, data: ManualOperationCreate, user: dict) -> Dict[str, Any]:
        """创建手动操作记录"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建手动操作记录
            manual_operation = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_manual_operation",
                f"创建手动操作记录: {manual_operation.username}",
                extra={"manual_operation_id": manual_operation.id, "username": manual_operation.username}
            )

            return ApiResponse.success(
                data=self._format_manual_operation_response(manual_operation),
                message="手动操作记录创建成功"
            )

        except Exception as e:
            logger.error(f"创建手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"创建手动操作记录失败: {str(e)}")

    async def get_manual_operation_by_id(self, operation_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取手动操作记录"""
        try:
            manual_operation = await self.repo.get_by_id(operation_id)
            if not manual_operation:
                raise ResourceNotFoundError(f"手动操作记录ID '{operation_id}' 不存在")

            return ApiResponse.success(
                data=self._format_manual_operation_response(manual_operation),
                message="获取手动操作记录成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取手动操作记录失败: {str(e)}")

    async def get_manual_operations(self, query: ManualOperationQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取手动操作记录列表"""
        try:
            manual_operations, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                user_id=query.user_id,
                username=query.username,
                start_time=query.start_time,
                end_time=query.end_time
            )

            return ApiResponse.paginated(
                items=[self._format_manual_operation_response(operation) for operation in manual_operations],
                total=total,
                page=query.page,
                size=query.size,
                message="获取手动操作记录列表成功"
            )

        except Exception as e:
            logger.error(f"获取手动操作记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取手动操作记录列表失败: {str(e)}")

    async def update_manual_operation(self, operation_id: str, data: ManualOperationUpdate, user: dict) -> Dict[str, Any]:
        """更新手动操作记录"""
        try:
            # 检查手动操作记录是否存在
            existing_operation = await self.repo.get_by_id(operation_id)
            if not existing_operation:
                raise ResourceNotFoundError(f"手动操作记录ID '{operation_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新手动操作记录
            manual_operation = await self.repo.update(operation_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_manual_operation",
                f"更新手动操作记录: {manual_operation.username}",
                extra={"manual_operation_id": manual_operation.id, "username": manual_operation.username}
            )

            return ApiResponse.success(
                data=self._format_manual_operation_response(manual_operation),
                message="手动操作记录更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"更新手动操作记录失败: {str(e)}")

    async def delete_manual_operation(self, operation_id: str, user: dict) -> Dict[str, Any]:
        """删除手动操作记录"""
        try:
            # 检查手动操作记录是否存在
            existing_operation = await self.repo.get_by_id(operation_id)
            if not existing_operation:
                raise ResourceNotFoundError(f"手动操作记录ID '{operation_id}' 不存在")

            # 软删除手动操作记录
            success = await self.repo.soft_delete(operation_id, user["username"])
            if not success:
                raise BusinessError(f"删除手动操作记录失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_manual_operation",
                f"删除手动操作记录: {existing_operation.username}",
                extra={"manual_operation_id": operation_id, "username": existing_operation.username}
            )

            return ApiResponse.success(
                data={"id": operation_id},
                message="手动操作记录删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"删除手动操作记录失败: {str(e)}")

    async def get_manual_operation_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取手动操作记录统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取手动操作记录统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取手动操作记录统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取手动操作记录统计信息失败: {str(e)}")

    async def get_manual_operations_by_ids(self, operation_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取手动操作记录"""
        try:
            manual_operations = await self.repo.get_by_ids(operation_ids)
            
            if not manual_operations:
                raise ResourceNotFoundError("未找到任何手动操作记录")

            return ApiResponse.success(
                data=[self._format_manual_operation_response(operation) for operation in manual_operations],
                message="获取手动操作记录成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"根据ID列表获取手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取手动操作记录失败: {str(e)}")

    async def get_manual_operations_by_user(self, user_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据用户ID获取手动操作记录"""
        try:
            manual_operations = await self.repo.get_by_user_id(user_id)
            
            return ApiResponse.success(
                data=[self._format_manual_operation_response(operation) for operation in manual_operations],
                message="获取用户手动操作记录成功"
            )

        except Exception as e:
            logger.error(f"根据用户ID获取手动操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取手动操作记录失败: {str(e)}")

    def _format_manual_operation_response(self, manual_operation) -> Dict[str, Any]:
        """格式化手动操作记录响应数据"""
        return {
            "id": manual_operation.id,
            "user_id": manual_operation.user_id,
            "username": manual_operation.username,
            "operation_time": manual_operation.operation_time.strftime("%Y-%m-%dT%H:%M:%S") if manual_operation.operation_time else None,
            "operation_content": manual_operation.operation_content,
            "created_at": manual_operation.created_at.strftime("%Y-%m-%dT%H:%M:%S") if manual_operation.created_at else None,
            "updated_at": manual_operation.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if manual_operation.updated_at else None,
            "created_by": manual_operation.created_by,
            "updated_by": manual_operation.updated_by,
        }
