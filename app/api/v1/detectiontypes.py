"""
检测类型API路由
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission
from ...services.detectiontype_service import DetectionTypeService
from ...schemas.detectiontype import (
    DetectionTypeCreate,
    DetectionTypeUpdate,
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_detection_type(
    detection_type_data: DetectionTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建检测类型
    
    Args:
        detection_type_data: 检测类型创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的检测类型对象
    """
    service = DetectionTypeService(db)
    return await service.create_detection_type(detection_type_data, current_user)


@router.get("/", response_model=dict)
async def get_detection_types(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    type_name: Optional[str] = Query(None, description="检测类型名称（模糊查询）"),
    type_code: Optional[str] = Query(None, description="检测类型代码（精确查询）"),
    enabled: Optional[bool] = Query(None, description="启用状态（筛选）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取检测类型列表
    
    Args:
        page: 页码
        size: 每页数量
        type_name: 检测类型名称（模糊查询）
        type_code: 检测类型代码（精确查询）
        enabled: 启用状态（筛选）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        检测类型列表
    """
    service = DetectionTypeService(db)
    return await service.get_detection_types(
        page=page,
        size=size,
        type_name=type_name,
        type_code=type_code,
        enabled=enabled,
    )


@router.get("/{detection_type_id}", response_model=dict)
async def get_detection_type_by_id(
    detection_type_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取检测类型
    
    Args:
        detection_type_id: 检测类型ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        检测类型对象
    """
    service = DetectionTypeService(db)
    return await service.get_detection_type_by_id(detection_type_id)


@router.put("/{detection_type_id}", response_model=dict)
async def update_detection_type(
    detection_type_id: str,
    detection_type_data: DetectionTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新检测类型
    
    Args:
        detection_type_id: 检测类型ID
        detection_type_data: 检测类型更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的检测类型对象
    """
    service = DetectionTypeService(db)
    return await service.update_detection_type(detection_type_id, detection_type_data, current_user)


@router.delete("/{detection_type_id}", response_model=dict)
async def delete_detection_type(
    detection_type_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除检测类型
    
    Args:
        detection_type_id: 检测类型ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = DetectionTypeService(db)
    return await service.delete_detection_type(detection_type_id, current_user)

