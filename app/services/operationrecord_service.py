"""
操作记录业务逻辑服务
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from datetime import datetime

from ..repositories.operationrecord_repository import OperationRecordRepository
from ..schemas.operationrecord import OperationRecordCreate, OperationRecordUpdate, OperationRecordQuery
from ..core.exceptions import (
    ResourceNotFoundError, BusinessError
)
from ..utils.response import ApiResponse
from ..config.logging import get_logger, log_user_action

logger = get_logger(__name__)


class OperationRecordService:
    """操作记录业务逻辑服务"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = OperationRecordRepository(db)

    async def create_operation_record(self, data: OperationRecordCreate, user: dict) -> Dict[str, Any]:
        """创建操作记录"""
        try:
            # 准备创建数据
            create_data = {
                **data.dict(),
                "created_by": user["username"],
                "updated_by": user["username"]
            }

            # 创建操作记录
            operation_record = await self.repo.create(create_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "create_operation_record",
                f"创建操作记录: {operation_record.username}",
                extra={"operation_record_id": operation_record.id, "username": operation_record.username}
            )

            return ApiResponse.success(
                data=self._format_operation_record_response(operation_record),
                message="操作记录创建成功"
            )

        except Exception as e:
            logger.error(f"创建操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"创建操作记录失败: {str(e)}")

    async def get_operation_record_by_id(self, record_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据ID获取操作记录"""
        try:
            operation_record = await self.repo.get_by_id(record_id)
            if not operation_record:
                raise ResourceNotFoundError(f"操作记录ID '{record_id}' 不存在")

            return ApiResponse.success(
                data=self._format_operation_record_response(operation_record),
                message="获取操作记录成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取操作记录失败: {str(e)}")

    async def get_operation_records(self, query: OperationRecordQuery, user: Optional[dict]) -> Dict[str, Any]:
        """获取操作记录列表"""
        try:
            operation_records, total = await self.repo.get_all(
                page=query.page,
                size=query.size,
                user_id=query.user_id,
                username=query.username,
                start_time=query.start_time,
                end_time=query.end_time
            )

            return ApiResponse.paginated(
                items=[self._format_operation_record_response(record) for record in operation_records],
                total=total,
                page=query.page,
                size=query.size,
                message="获取操作记录列表成功"
            )

        except Exception as e:
            logger.error(f"获取操作记录列表失败: {e}", exc_info=True)
            raise BusinessError(f"获取操作记录列表失败: {str(e)}")

    async def update_operation_record(self, record_id: str, data: OperationRecordUpdate, user: dict) -> Dict[str, Any]:
        """更新操作记录"""
        try:
            # 检查操作记录是否存在
            existing_record = await self.repo.get_by_id(record_id)
            if not existing_record:
                raise ResourceNotFoundError(f"操作记录ID '{record_id}' 不存在")

            # 准备更新数据
            update_data = {k: v for k, v in data.dict().items() if v is not None}
            update_data["updated_by"] = user["username"]

            # 更新操作记录
            operation_record = await self.repo.update(record_id, update_data)
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "update_operation_record",
                f"更新操作记录: {operation_record.username}",
                extra={"operation_record_id": operation_record.id, "username": operation_record.username}
            )

            return ApiResponse.success(
                data=self._format_operation_record_response(operation_record),
                message="操作记录更新成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"更新操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"更新操作记录失败: {str(e)}")

    async def delete_operation_record(self, record_id: str, user: dict) -> Dict[str, Any]:
        """删除操作记录"""
        try:
            # 检查操作记录是否存在
            existing_record = await self.repo.get_by_id(record_id)
            if not existing_record:
                raise ResourceNotFoundError(f"操作记录ID '{record_id}' 不存在")

            # 软删除操作记录
            success = await self.repo.soft_delete(record_id, user["username"])
            if not success:
                raise BusinessError(f"删除操作记录失败: 软删除操作返回失败")
            
            # 记录操作日志
            log_user_action(
                logger, user["username"], "delete_operation_record",
                f"删除操作记录: {existing_record.username}",
                extra={"operation_record_id": record_id, "username": existing_record.username}
            )

            return ApiResponse.success(
                data={"id": record_id},
                message="操作记录删除成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"删除操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"删除操作记录失败: {str(e)}")

    async def get_operation_record_stats(self, user: Optional[dict]) -> Dict[str, Any]:
        """获取操作记录统计信息"""
        try:
            stats = await self.repo.get_stats()
            return ApiResponse.success(
                data=stats,
                message="获取操作记录统计信息成功"
            )

        except Exception as e:
            logger.error(f"获取操作记录统计信息失败: {e}", exc_info=True)
            raise BusinessError(f"获取操作记录统计信息失败: {str(e)}")

    async def get_operation_records_by_ids(self, record_ids: List[str], user: Optional[dict]) -> Dict[str, Any]:
        """根据ID列表获取操作记录"""
        try:
            operation_records = await self.repo.get_by_ids(record_ids)
            
            if not operation_records:
                raise ResourceNotFoundError("未找到任何操作记录")

            return ApiResponse.success(
                data=[self._format_operation_record_response(record) for record in operation_records],
                message="获取操作记录成功"
            )

        except ResourceNotFoundError:
            raise
        except Exception as e:
            logger.error(f"根据ID列表获取操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取操作记录失败: {str(e)}")

    async def get_operation_records_by_user(self, user_id: str, user: Optional[dict]) -> Dict[str, Any]:
        """根据用户ID获取操作记录"""
        try:
            operation_records = await self.repo.get_by_user_id(user_id)
            
            return ApiResponse.success(
                data=[self._format_operation_record_response(record) for record in operation_records],
                message="获取用户操作记录成功"
            )

        except Exception as e:
            logger.error(f"根据用户ID获取操作记录失败: {e}", exc_info=True)
            raise BusinessError(f"获取操作记录失败: {str(e)}")

    def _format_operation_record_response(self, operation_record) -> Dict[str, Any]:
        """格式化操作记录响应数据"""
        return {
            "id": operation_record.id,
            "user_id": operation_record.user_id,
            "username": operation_record.username,
            "operation_time": operation_record.operation_time.strftime("%Y-%m-%dT%H:%M:%S") if operation_record.operation_time else None,
            "operation_content": operation_record.operation_content,
            "created_at": operation_record.created_at.strftime("%Y-%m-%dT%H:%M:%S") if operation_record.created_at else None,
            "updated_at": operation_record.updated_at.strftime("%Y-%m-%dT%H:%M:%S") if operation_record.updated_at else None,
            "created_by": operation_record.created_by,
            "updated_by": operation_record.updated_by,
        }
