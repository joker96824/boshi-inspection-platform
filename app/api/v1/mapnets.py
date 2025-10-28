"""
地图路网管理API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.mapnet_service import MapNetService
from ...schemas.mapnet import (
    MapNetCreate, MapNetUpdate, MapNetResponse, MapNetQuery, MapNetListResponse
)
from ...config.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/", response_model=dict)
async def create_mapnet(
    mapnet_data: MapNetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建地图路网元素
    
    Args:
        mapnet_data: 路网元素创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建结果
    
    Raises:
        400: 数据验证失败
        401: 用户未认证
        403: 无权限访问指定地图
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.create_mapnet(mapnet_data, current_user)


@router.get("/", response_model=dict)
async def get_mapnets_by_map(
    map_id: str = Query(..., description="地图ID"),
    map_net_type: Optional[str] = Query(None, description="元素类型（模糊匹配）"),
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取地图的路网元素列表
    
    Args:
        map_id: 地图ID
        map_net_type: 元素类型模糊匹配（可选）
        page: 页码
        size: 每页数量
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        路网元素列表（分页）
    
    Raises:
        401: 用户未认证
        403: 无权限访问指定地图
    """
    query = MapNetQuery(map_id=map_id, map_net_type=map_net_type, page=page, size=size)
    mapnet_service = MapNetService(db)
    return await mapnet_service.get_mapnets_by_map(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_mapnets_by_ids(
    mapnet_ids: List[str] = Query(..., description="路网元素ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询路网元素
    
    支持单个或多个ID查询
    
    Args:
        mapnet_ids: 路网元素ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        路网元素列表
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.get_mapnets_by_ids(mapnet_ids, current_user)


@router.get("/{mapnet_id}", response_model=dict)
async def get_mapnet_by_id(
    mapnet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取路网元素详情
    
    Args:
        mapnet_id: 路网元素ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        路网元素详情
    
    Raises:
        404: 路网元素不存在
        401: 用户未认证
        403: 无权限访问该路网元素
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.get_mapnet_by_id(mapnet_id, current_user)


@router.put("/{mapnet_id}", response_model=dict)
async def update_mapnet(
    mapnet_id: str,
    mapnet_data: MapNetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新路网元素信息
    
    Args:
        mapnet_id: 路网元素ID
        mapnet_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新结果
    
    Raises:
        404: 路网元素不存在
        401: 用户未认证
        403: 无权限访问该路网元素
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.update_mapnet(mapnet_id, mapnet_data, current_user)


@router.delete("/{mapnet_id}", response_model=dict)
async def delete_mapnet(
    mapnet_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除路网元素
    
    Args:
        mapnet_id: 路网元素ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    
    Raises:
        404: 路网元素不存在
        401: 用户未认证
        403: 无权限访问该路网元素
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.delete_mapnet(mapnet_id, current_user)


@router.get("/stats/{map_id}", response_model=dict)
async def get_mapnet_stats(
    map_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取地图的路网统计信息
    
    Args:
        map_id: 地图ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        路网统计信息
    
    Raises:
        401: 用户未认证
        403: 无权限访问指定地图
    """
    mapnet_service = MapNetService(db)
    return await mapnet_service.get_mapnet_stats(map_id, current_user)
