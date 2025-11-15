"""
设备API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.device_service import DeviceService
from ...schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse, DeviceQuery, DeviceListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_device(
    device_data: DeviceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建设备
    
    Args:
        device_data: 设备创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的设备信息
    """
    service = DeviceService(db)
    return await service.create_device(device_data, current_user)


@router.get("/", response_model=dict)
async def get_devices(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    device_name: Optional[str] = Query(None, description="设备名称（模糊查询）"),
    point_id: Optional[str] = Query(None, description="巡检点ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取设备列表
    
    Args:
        page: 页码
        size: 每页数量
        device_name: 设备名称（模糊查询）
        map_id: 地图ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        设备列表和分页信息
    """
    validate_pagination_params(page, size)
    query = DeviceQuery(
        page=page,
        size=size,
        device_name=device_name,
        point_id=point_id
    )
    service = DeviceService(db)
    return await service.get_devices(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_devices_by_ids(
    device_ids: List[str] = Query(..., description="设备ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询设备
    
    支持单个或多个ID查询
    
    Args:
        device_ids: 设备ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        设备列表
    """
    service = DeviceService(db)
    return await service.get_devices_by_ids(device_ids, current_user)


@router.get("/{device_id}", response_model=dict)
async def get_device_by_id(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取设备详情
    
    Args:
        device_id: 设备ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        设备详情
    """
    service = DeviceService(db)
    return await service.get_device_by_id(device_id, current_user)


@router.put("/{device_id}", response_model=dict)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新设备
    
    Args:
        device_id: 设备ID
        device_data: 设备更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的设备信息
    """
    service = DeviceService(db)
    return await service.update_device(device_id, device_data, current_user)


@router.delete("/{device_id}", response_model=dict)
async def delete_device(
    device_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除设备
    
    Args:
        device_id: 设备ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = DeviceService(db)
    return await service.delete_device(device_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_device_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取设备统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        设备统计信息
    """
    service = DeviceService(db)
    return await service.get_device_stats(current_user)

