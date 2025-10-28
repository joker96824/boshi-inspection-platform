"""
环境传感器API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.environment_sensor_service import EnvironmentSensorService
from ...schemas.environmentsensor import (
    EnvironmentSensorCreate, EnvironmentSensorUpdate, EnvironmentSensorResponse, 
    EnvironmentSensorQuery, EnvironmentSensorListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_environment_sensors(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    station_number: Optional[int] = Query(None, description="站号筛选"),
    baud_rate: Optional[int] = Query(None, description="波特率筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取环境传感器列表"""
    query = EnvironmentSensorQuery(
        page=page,
        size=size,
        station_number=station_number,
        baud_rate=baud_rate
    )
    
    service = EnvironmentSensorService(db)
    return await service.get_sensors(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_environment_sensors_by_ids(
    environmentsensor_ids: List[str] = Query(..., description="环境传感器ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取环境传感器"""
    service = EnvironmentSensorService(db)
    return await service.get_sensors_by_ids(environmentsensor_ids, current_user)


@router.get("/{sensor_id}", response_model=dict)
async def get_environment_sensor_by_id(
    sensor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取环境传感器"""
    service = EnvironmentSensorService(db)
    return await service.get_sensor_by_id(sensor_id, current_user)


@router.post("/", response_model=dict)
async def create_environment_sensor(
    data: EnvironmentSensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建环境传感器"""
    service = EnvironmentSensorService(db)
    return await service.create_sensor(data, current_user)


@router.put("/{sensor_id}", response_model=dict)
async def update_environment_sensor(
    sensor_id: str,
    data: EnvironmentSensorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新环境传感器"""
    service = EnvironmentSensorService(db)
    return await service.update_sensor(sensor_id, data, current_user)


@router.delete("/{sensor_id}", response_model=dict)
async def delete_environment_sensor(
    sensor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除环境传感器"""
    service = EnvironmentSensorService(db)
    return await service.delete_sensor(sensor_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_environment_sensor_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取环境传感器统计信息"""
    service = EnvironmentSensorService(db)
    return await service.get_sensor_stats(current_user)

