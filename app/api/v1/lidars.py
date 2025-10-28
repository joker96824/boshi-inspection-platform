"""
激光雷达配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.lidar_service import LidarService
from ...schemas.lidar import (
    LidarCreate, LidarUpdate, LidarResponse, 
    LidarQuery, LidarListResponse
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_lidars(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    lidar_ip: Optional[str] = Query(None, description="激光雷达IP筛选"),
    lidar_port: Optional[int] = Query(None, description="激光雷达端口筛选"),
    scan_frequency_rpm: Optional[int] = Query(None, description="扫描频率筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取激光雷达配置列表"""
    query = LidarQuery(
        page=page,
        size=size,
        lidar_ip=lidar_ip,
        lidar_port=lidar_port,
        scan_frequency_rpm=scan_frequency_rpm
    )
    
    service = LidarService(db)
    return await service.get_lidars(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_lidars_by_ids(
    lidar_ids: List[str] = Query(..., description="激光雷达配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取激光雷达配置"""
    service = LidarService(db)
    return await service.get_lidars_by_ids(lidar_ids, current_user)


@router.get("/{lidar_id}", response_model=dict)
async def get_lidar_by_id(
    lidar_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取激光雷达配置"""
    service = LidarService(db)
    return await service.get_lidar_by_id(lidar_id, current_user)


@router.post("/", response_model=dict)
async def create_lidar(
    data: LidarCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建激光雷达配置"""
    service = LidarService(db)
    return await service.create_lidar(data, current_user)


@router.put("/{lidar_id}", response_model=dict)
async def update_lidar(
    lidar_id: str,
    data: LidarUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新激光雷达配置"""
    service = LidarService(db)
    return await service.update_lidar(lidar_id, data, current_user)


@router.delete("/{lidar_id}", response_model=dict)
async def delete_lidar(
    lidar_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除激光雷达配置"""
    service = LidarService(db)
    return await service.delete_lidar(lidar_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_lidar_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取激光雷达配置统计信息"""
    service = LidarService(db)
    return await service.get_lidar_stats(current_user)
