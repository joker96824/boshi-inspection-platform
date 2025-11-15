"""
传感器记录API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.sensorhistory_service import SensorHistoryService
from ...schemas.sensorhistory import SensorHistoryCreate, SensorHistoryUpdate, SensorHistoryResponse, SensorHistoryQuery, SensorHistoryListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_sensor_history(
    history_data: SensorHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建传感器记录
    
    Args:
        history_data: 传感器记录创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的传感器记录信息
    """
    service = SensorHistoryService(db)
    return await service.create_sensor_history(history_data, current_user)


@router.get("/", response_model=dict)
async def get_sensor_histories(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    sensor_id: Optional[str] = Query(None, description="传感器ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取传感器记录列表
    
    Args:
        page: 页码
        size: 每页数量
        sensor_id: 传感器ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器记录列表和分页信息
    """
    query = SensorHistoryQuery(
        page=page,
        size=size,
        sensor_id=sensor_id
    )
    service = SensorHistoryService(db)
    return await service.get_sensor_histories(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_sensor_histories_by_ids(
    sensorhistory_ids: List[str] = Query(..., description="传感器记录ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询传感器记录
    
    支持单个或多个ID查询
    
    Args:
        sensorhistory_ids: 传感器记录ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器记录列表
    """
    service = SensorHistoryService(db)
    return await service.get_sensor_histories_by_ids(sensorhistory_ids, current_user)


@router.get("/{history_id}", response_model=dict)
async def get_sensor_history_by_id(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取传感器记录详情
    
    Args:
        history_id: 传感器记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器记录详情
    """
    service = SensorHistoryService(db)
    return await service.get_sensor_history_by_id(history_id, current_user)


@router.put("/{history_id}", response_model=dict)
async def update_sensor_history(
    history_id: str,
    history_data: SensorHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新传感器记录
    
    Args:
        history_id: 传感器记录ID
        history_data: 传感器记录更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的传感器记录信息
    """
    service = SensorHistoryService(db)
    return await service.update_sensor_history(history_id, history_data, current_user)


@router.delete("/{history_id}", response_model=dict)
async def delete_sensor_history(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除传感器记录
    
    Args:
        history_id: 传感器记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = SensorHistoryService(db)
    return await service.delete_sensor_history(history_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_sensor_history_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取传感器记录统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        传感器记录统计信息
    """
    service = SensorHistoryService(db)
    return await service.get_sensor_history_stats(current_user)
