"""
云台日程API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.gimbalschedule_service import GimbalScheduleService
from ...schemas.gimbalschedule import (
    GimbalScheduleCreate, GimbalScheduleUpdate, GimbalScheduleResponse, 
    GimbalScheduleQuery, GimbalScheduleListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal_schedule(
    schedule_data: GimbalScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建云台日程
    
    Args:
        schedule_data: 云台日程创建数据（后端格式）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的云台日程信息
    """
    service = GimbalScheduleService(db)
    return await service.create_gimbal_schedule(schedule_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbal_schedules(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    cycle_type: Optional[str] = Query(None, description="周期类型筛选：daily/monthly_days/weekly"),
    enabled: Optional[bool] = Query(None, description="启用状态筛选"),
    gimbaltask_id: Optional[str] = Query(None, description="云台任务ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台日程列表
    
    Args:
        page: 页码
        size: 每页数量
        cycle_type: 周期类型筛选
        enabled: 启用状态筛选
        gimbaltask_id: 云台任务ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台日程列表和分页信息
    """
    query = GimbalScheduleQuery(
        page=page,
        size=size,
        cycle_type=cycle_type,
        enabled=enabled,
        gimbaltask_id=gimbaltask_id
    )
    service = GimbalScheduleService(db)
    return await service.get_gimbal_schedules(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbal_schedules_by_ids(
    gimbalschedule_ids: List[str] = Query(..., description="云台日程ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询云台日程
    
    支持单个或多个ID查询
    
    Args:
        gimbalschedule_ids: 云台日程ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台日程列表
    """
    service = GimbalScheduleService(db)
    return await service.get_gimbal_schedules_by_ids(gimbalschedule_ids, current_user)


@router.get("/{schedule_id}", response_model=dict)
async def get_gimbal_schedule_by_id(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取云台日程详情
    
    Args:
        schedule_id: 云台日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台日程详情
    """
    service = GimbalScheduleService(db)
    return await service.get_gimbal_schedule_by_id(schedule_id, current_user)


@router.put("/{schedule_id}", response_model=dict)
async def update_gimbal_schedule(
    schedule_id: str,
    schedule_data: GimbalScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新云台日程
    
    Args:
        schedule_id: 云台日程ID
        schedule_data: 云台日程更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的云台日程信息
    """
    service = GimbalScheduleService(db)
    return await service.update_gimbal_schedule(schedule_id, schedule_data, current_user)


@router.delete("/{schedule_id}", response_model=dict)
async def delete_gimbal_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除云台日程
    
    Args:
        schedule_id: 云台日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = GimbalScheduleService(db)
    return await service.delete_gimbal_schedule(schedule_id, current_user)


@router.get("/by-date", response_model=dict)
async def get_gimbal_schedules_by_date(
    date: str = Query(..., description="日期 (YYYY-MM-DD)"),
    gimbal_ids: Optional[List[str]] = Query(None, description="云台ID列表筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取指定日期的所有云台日程（支持按云台ID筛选）
    
    通过地图ID和机器人ID获取所有相关云台的当天日程
    
    Args:
        date: 日期（YYYY-MM-DD格式）
        gimbal_ids: 云台ID列表（可选，用于过滤特定云台）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        指定日期的云台日程列表
    """
    service = GimbalScheduleService(db)
    return await service.get_schedules_by_date(date, gimbal_ids, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_schedule_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台日程统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台日程统计信息
    """
    service = GimbalScheduleService(db)
    return await service.get_gimbal_schedule_stats(current_user)
