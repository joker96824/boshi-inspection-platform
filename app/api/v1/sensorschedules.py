"""
传感器日程API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.sensorschedule_service import SensorScheduleService
from ...schemas.sensorschedule import SensorScheduleCreate, SensorScheduleUpdate, SensorScheduleResponse, SensorScheduleQuery, SensorScheduleListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_sensor_schedule(
    schedule_data: SensorScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建传感器日程
    
    Args:
        schedule_data: 传感器日程创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的传感器日程信息
    """
    service = SensorScheduleService(db)
    return await service.create_sensor_schedule(schedule_data, current_user)


@router.get("/", response_model=dict)
async def get_sensor_schedules(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    schedule_type: Optional[str] = Query(None, description="传感器日程类型筛选"),
    schedule_is_active: Optional[bool] = Query(None, description="激活状态筛选"),
    sensor_id: Optional[str] = Query(None, description="传感器ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取传感器日程列表
    
    Args:
        page: 页码
        size: 每页数量
        schedule_type: 传感器日程类型筛选
        schedule_is_active: 激活状态筛选
        sensor_id: 传感器ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器日程列表和分页信息
    """
    query = SensorScheduleQuery(
        page=page,
        size=size,
        schedule_type=schedule_type,
        schedule_is_active=schedule_is_active,
        sensor_id=sensor_id
    )
    service = SensorScheduleService(db)
    return await service.get_sensor_schedules(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_sensor_schedules_by_ids(
    sensorschedule_ids: List[str] = Query(..., description="传感器日程ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询传感器日程
    
    支持单个或多个ID查询
    
    Args:
        sensorschedule_ids: 传感器日程ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器日程列表
    """
    service = SensorScheduleService(db)
    return await service.get_sensor_schedules_by_ids(sensorschedule_ids, current_user)


@router.get("/{schedule_id}", response_model=dict)
async def get_sensor_schedule_by_id(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取传感器日程详情
    
    Args:
        schedule_id: 传感器日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器日程详情
    """
    service = SensorScheduleService(db)
    return await service.get_sensor_schedule_by_id(schedule_id, current_user)


@router.put("/{schedule_id}", response_model=dict)
async def update_sensor_schedule(
    schedule_id: str,
    schedule_data: SensorScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新传感器日程
    
    Args:
        schedule_id: 传感器日程ID
        schedule_data: 传感器日程更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的传感器日程信息
    """
    service = SensorScheduleService(db)
    return await service.update_sensor_schedule(schedule_id, schedule_data, current_user)


@router.delete("/{schedule_id}", response_model=dict)
async def delete_sensor_schedule(
    schedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除传感器日程
    
    Args:
        schedule_id: 传感器日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = SensorScheduleService(db)
    return await service.delete_sensor_schedule(schedule_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_sensor_schedule_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取传感器日程统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器日程统计信息
    """
    service = SensorScheduleService(db)
    return await service.get_sensor_schedule_stats(current_user)
