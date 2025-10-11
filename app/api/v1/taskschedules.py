"""
任务日程API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission
from ...services.taskschedule_service import TaskScheduleService
from ...schemas.taskschedule import TaskScheduleCreate, TaskScheduleUpdate

router = APIRouter()


@router.post("/", response_model=dict)
async def create_taskschedule(
    taskschedule_data: TaskScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建任务日程
    
    Args:
        taskschedule_data: 任务日程创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的任务日程信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.create_taskschedule(taskschedule_data, current_user)


@router.get("/", response_model=dict)
async def get_taskschedules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_id: str = Query(None, description="任务ID"),
    schedule_type: str = Query(None, description="日程类型（模糊匹配）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取任务日程列表
    
    Args:
        page: 页码
        size: 每页数量
        task_id: 任务ID
        schedule_type: 日程类型（模糊匹配）
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程列表
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedules(
        current_user, page, size, task_id, schedule_type
    )


@router.get("/by-ids", response_model=dict)
async def get_taskschedules_by_ids(
    taskschedule_ids: List[str] = Query(..., description="任务日程ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID列表查询任务日程
    
    支持单个或多个ID查询
    
    Args:
        taskschedule_ids: 任务日程ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程列表
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedules_by_ids(taskschedule_ids, current_user)


@router.get("/{taskschedule_id}", response_model=dict)
async def get_taskschedule_by_id(
    taskschedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程详情
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedule_by_id(taskschedule_id, current_user)


@router.put("/{taskschedule_id}", response_model=dict)
async def update_taskschedule(
    taskschedule_id: str,
    taskschedule_data: TaskScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        taskschedule_data: 任务日程更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的任务日程信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.update_taskschedule(taskschedule_id, taskschedule_data, current_user)


@router.delete("/{taskschedule_id}", response_model=dict)
async def delete_taskschedule(
    taskschedule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除任务日程
    
    Args:
        taskschedule_id: 任务日程ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.delete_taskschedule(taskschedule_id, current_user)


@router.get("/stats/{task_id}", response_model=dict)
async def get_taskschedule_stats(
    task_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取任务日程统计信息
    
    Args:
        task_id: 任务ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务日程统计信息
    """
    taskschedule_service = TaskScheduleService(db)
    return await taskschedule_service.get_taskschedule_stats(task_id, current_user)
