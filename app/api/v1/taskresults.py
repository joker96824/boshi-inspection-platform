"""
任务结果API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission, require_no_auth
from ...services.taskresult_service import TaskResultService
from ...schemas.taskresult import (
    TaskResultCreate, TaskResultUpdate, TaskResultQuery,
    TaskResultResponse, TaskResultListResponse
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_taskresult(
    taskresult_data: TaskResultCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建任务结果
    
    Args:
        taskresult_data: 任务结果创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的任务结果对象
    """
    service = TaskResultService(db)
    return await service.create_taskresult(taskresult_data, current_user)


@router.get("/by-ids", response_model=dict)
async def get_taskresults_by_ids(
    taskresult_ids: List[str] = Query(..., description="任务结果ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询任务结果
    
    支持单个或多个ID查询
    
    Args:
        taskresult_ids: 任务结果ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务结果列表
    """
    service = TaskResultService(db)
    return await service.get_taskresults_by_ids(taskresult_ids, current_user)


@router.get("/", response_model=dict)
async def get_taskresults(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """分页查询任务结果列表
    
    Args:
        page: 页码
        size: 每页数量
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分页的任务结果列表
    """
    service = TaskResultService(db)
    query = TaskResultQuery(page=page, size=size)
    return await service.get_taskresults(query, current_user)


@router.get("/{taskresult_id}", response_model=dict)
async def get_taskresult_by_id(
    taskresult_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取任务结果
    
    Args:
        taskresult_id: 任务结果ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务结果对象
    """
    service = TaskResultService(db)
    return await service.get_taskresult_by_id(taskresult_id, current_user)


@router.put("/{taskresult_id}", response_model=dict)
async def update_taskresult(
    taskresult_id: str,
    taskresult_data: TaskResultUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新任务结果
    
    Args:
        taskresult_id: 任务结果ID
        taskresult_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的任务结果对象
    """
    service = TaskResultService(db)
    return await service.update_taskresult(taskresult_id, taskresult_data, current_user)


@router.delete("/{taskresult_id}", response_model=dict)
async def delete_taskresult(
    taskresult_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除任务结果（软删除）
    
    Args:
        taskresult_id: 任务结果ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = TaskResultService(db)
    return await service.delete_taskresult(taskresult_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_taskresult_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取任务结果统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        统计信息
    """
    service = TaskResultService(db)
    return await service.get_taskresult_stats(current_user)
