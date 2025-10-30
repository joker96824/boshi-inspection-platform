"""
操作记录API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.operationrecord_service import OperationRecordService
from ...schemas.operationrecord import (
    OperationRecordCreate, OperationRecordResponse, 
    OperationRecordQuery, OperationRecordListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_operation_records(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    user_id: Optional[str] = Query(None, description="用户ID筛选"),
    username: Optional[str] = Query(None, description="用户名筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间筛选"),
    end_time: Optional[datetime] = Query(None, description="结束时间筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取操作记录列表"""
    query = OperationRecordQuery(
        page=page,
        size=size,
        user_id=user_id,
        username=username,
        start_time=start_time,
        end_time=end_time
    )
    
    service = OperationRecordService(db)
    return await service.get_operation_records(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_operation_records_by_ids(
    operationrecord_ids: List[str] = Query(..., description="操作记录ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取操作记录"""
    service = OperationRecordService(db)
    return await service.get_operation_records_by_ids(operationrecord_ids, current_user)


@router.get("/by-user/{user_id}", response_model=dict)
async def get_operation_records_by_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据用户ID获取操作记录"""
    service = OperationRecordService(db)
    return await service.get_operation_records_by_user(user_id, current_user)


@router.get("/{record_id}", response_model=dict)
async def get_operation_record_by_id(
    record_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取操作记录"""
    service = OperationRecordService(db)
    return await service.get_operation_record_by_id(record_id, current_user)


@router.post("/", response_model=dict)
async def create_operation_record(
    data: OperationRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建操作记录"""
    service = OperationRecordService(db)
    return await service.create_operation_record(data, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_operation_record_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取操作记录统计信息"""
    service = OperationRecordService(db)
    return await service.get_operation_record_stats(current_user)
