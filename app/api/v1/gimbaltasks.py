"""
云台任务API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.gimbaltask_service import GimbalTaskService
from ...schemas.gimbaltask import GimbalTaskCreate, GimbalTaskUpdate, GimbalTaskResponse, GimbalTaskQuery, GimbalTaskListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal_task(
    task_data: GimbalTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建云台任务
    
    Args:
        task_data: 云台任务创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的云台任务信息
    """
    service = GimbalTaskService(db)
    return await service.create_gimbal_task(task_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbal_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_name: Optional[str] = Query(None, description="云台任务名称（模糊查询）"),
    task_type: Optional[str] = Query(None, description="任务类别筛选：image/video"),
    gimbal_id: Optional[str] = Query(None, description="云台ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台任务列表
    
    Args:
        page: 页码
        size: 每页数量
        task_name: 云台任务名称（模糊查询）
        task_type: 任务类别筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台任务列表和分页信息
    """
    query = GimbalTaskQuery(
        page=page,
        size=size,
        task_name=task_name,
        task_type=task_type,
        gimbal_id=gimbal_id
    )
    service = GimbalTaskService(db)
    return await service.get_gimbal_tasks(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbal_tasks_by_ids(
    gimbaltask_ids: List[str] = Query(..., description="云台任务ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询云台任务
    
    支持单个或多个ID查询
    
    Args:
        gimbaltask_ids: 云台任务ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台任务列表
    """
    service = GimbalTaskService(db)
    return await service.get_gimbal_tasks_by_ids(gimbaltask_ids, current_user)


@router.get("/{task_id}", response_model=dict)
async def get_gimbal_task_by_id(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取云台任务详情
    
    Args:
        task_id: 云台任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台任务详情
    """
    service = GimbalTaskService(db)
    return await service.get_gimbal_task_by_id(task_id, current_user)


@router.put("/{task_id}", response_model=dict)
async def update_gimbal_task(
    task_id: str,
    task_data: GimbalTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新云台任务
    
    Args:
        task_id: 云台任务ID
        task_data: 云台任务更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的云台任务信息
    """
    service = GimbalTaskService(db)
    return await service.update_gimbal_task(task_id, task_data, current_user)


@router.delete("/{task_id}", response_model=dict)
async def delete_gimbal_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除云台任务
    
    Args:
        task_id: 云台任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = GimbalTaskService(db)
    return await service.delete_gimbal_task(task_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_task_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台任务统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台任务统计信息
    """
    service = GimbalTaskService(db)
    return await service.get_gimbal_task_stats(current_user)
