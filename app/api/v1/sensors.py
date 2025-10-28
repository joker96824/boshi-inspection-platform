"""
智能传感器API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.sensor_service import SensorService
from ...schemas.sensor import SensorCreate, SensorUpdate, SensorResponse, SensorQuery, SensorListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_sensor(
    sensor_data: SensorCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建智能传感器
    
    Args:
        sensor_data: 智能传感器创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的智能传感器信息
    """
    service = SensorService(db)
    return await service.create_sensor(sensor_data, current_user)


@router.get("/", response_model=dict)
async def get_sensors(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    sensor_name: Optional[str] = Query(None, description="传感器名称（模糊查询）"),
    device_id: Optional[str] = Query(None, description="设备ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取智能传感器列表
    
    Args:
        page: 页码
        size: 每页数量
        sensor_name: 传感器名称（模糊查询）
        device_id: 设备ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        智能传感器列表和分页信息
    """
    query = SensorQuery(
        page=page,
        size=size,
        sensor_name=sensor_name,
        device_id=device_id
    )
    service = SensorService(db)
    return await service.get_sensors(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_sensors_by_ids(
    sensor_ids: List[str] = Query(..., description="智能传感器ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询智能传感器
    
    支持单个或多个ID查询
    
    Args:
        sensor_ids: 智能传感器ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        智能传感器列表
    """
    service = SensorService(db)
    return await service.get_sensors_by_ids(sensor_ids, current_user)


@router.get("/{sensor_id}", response_model=dict)
async def get_sensor_by_id(
    sensor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取智能传感器详情
    
    Args:
        sensor_id: 智能传感器ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        智能传感器详情
    """
    service = SensorService(db)
    return await service.get_sensor_by_id(sensor_id, current_user)


@router.put("/{sensor_id}", response_model=dict)
async def update_sensor(
    sensor_id: str,
    sensor_data: SensorUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新智能传感器
    
    Args:
        sensor_id: 智能传感器ID
        sensor_data: 智能传感器更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的智能传感器信息
    """
    service = SensorService(db)
    return await service.update_sensor(sensor_id, sensor_data, current_user)


@router.delete("/{sensor_id}", response_model=dict)
async def delete_sensor(
    sensor_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除智能传感器
    
    Args:
        sensor_id: 智能传感器ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = SensorService(db)
    return await service.delete_sensor(sensor_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_sensor_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取智能传感器统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        智能传感器统计信息
    """
    service = SensorService(db)
    return await service.get_sensor_stats(current_user)

