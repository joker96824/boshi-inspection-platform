"""
电机状态配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.motor_status_service import MotorStatusService
from ...schemas.motorstatus import (
    MotorStatusCreate, MotorStatusUpdate, MotorStatusResponse, 
    MotorStatusQuery, MotorStatusListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_motor_statuses(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    motor_id: Optional[int] = Query(None, description="电机ID筛选"),
    baud_rate: Optional[int] = Query(None, description="波特率筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取电机状态配置列表"""
    query = MotorStatusQuery(
        page=page,
        size=size,
        motor_id=motor_id,
        baud_rate=baud_rate
    )
    
    service = MotorStatusService(db)
    return await service.get_motor_statuses(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_motor_statuses_by_ids(
    motorstatus_ids: List[str] = Query(..., description="电机状态配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取电机状态配置"""
    service = MotorStatusService(db)
    return await service.get_motor_statuses_by_ids(motorstatus_ids, current_user)


@router.get("/{status_id}", response_model=dict)
async def get_motor_status_by_id(
    status_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取电机状态配置"""
    service = MotorStatusService(db)
    return await service.get_motor_status_by_id(status_id, current_user)


@router.post("/", response_model=dict)
async def create_motor_status(
    data: MotorStatusCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建电机状态配置"""
    service = MotorStatusService(db)
    return await service.create_motor_status(data, current_user)


@router.put("/{status_id}", response_model=dict)
async def update_motor_status(
    status_id: str,
    data: MotorStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新电机状态配置"""
    service = MotorStatusService(db)
    return await service.update_motor_status(status_id, data, current_user)


@router.delete("/{status_id}", response_model=dict)
async def delete_motor_status(
    status_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除电机状态配置"""
    service = MotorStatusService(db)
    return await service.delete_motor_status(status_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_motor_status_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取电机状态配置统计信息"""
    service = MotorStatusService(db)
    return await service.get_motor_status_stats(current_user)
