"""
深度相机配置API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_write_permission, require_no_auth
from ...services.depth_camera_service import DepthCameraService
from ...schemas.depthcamera import (
    DepthCameraCreate, DepthCameraUpdate, DepthCameraResponse, 
    DepthCameraQuery, DepthCameraListResponse, DepthCameraBatchUpdate
)
from ...utils.response import ApiResponse

router = APIRouter()


@router.get("/", response_model=dict)
async def get_depth_cameras(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    serial_port_id: Optional[int] = Query(None, description="串口ID筛选"),
    camera_mode: Optional[str] = Query(None, description="相机模式筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取深度相机配置列表"""
    query = DepthCameraQuery(
        page=page,
        size=size,
        serial_port_id=serial_port_id,
        camera_mode=camera_mode
    )
    
    service = DepthCameraService(db)
    return await service.get_depth_cameras(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_depth_cameras_by_ids(
    depthcamera_ids: List[str] = Query(..., description="深度相机配置ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表获取深度相机配置"""
    service = DepthCameraService(db)
    return await service.get_depth_cameras_by_ids(depthcamera_ids, current_user)


@router.get("/{camera_id}", response_model=dict)
async def get_depth_camera_by_id(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取深度相机配置"""
    service = DepthCameraService(db)
    return await service.get_depth_camera_by_id(camera_id, current_user)


@router.post("/", response_model=dict)
async def create_depth_camera(
    data: DepthCameraCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建深度相机配置"""
    service = DepthCameraService(db)
    return await service.create_depth_camera(data, current_user)


@router.put("/batch-update-by-robot", response_model=dict)
async def batch_update_depth_cameras_by_robot(
    data: DepthCameraBatchUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """批量更新机器人的深度相机配置（真删除旧数据后重新添加）"""
    service = DepthCameraService(db)
    return await service.batch_update_depth_cameras_by_robot(data.robot_id, data.configs, current_user)


@router.put("/{camera_id}", response_model=dict)
async def update_depth_camera(
    camera_id: str,
    data: DepthCameraUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新深度相机配置（单个，兼容旧接口）"""
    service = DepthCameraService(db)
    return await service.update_depth_camera(camera_id, data, current_user)


@router.delete("/{camera_id}", response_model=dict)
async def delete_depth_camera(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除深度相机配置"""
    service = DepthCameraService(db)
    return await service.delete_depth_camera(camera_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_depth_camera_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取深度相机配置统计信息"""
    service = DepthCameraService(db)
    return await service.get_depth_camera_stats(current_user)
