"""
任务记录API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db
from ...core.auth import get_current_user
from ...core.permissions import require_write_permission, require_read_permission
from ...services.taskhistory_service import TaskHistoryService
from ...schemas.taskhistory import TaskHistoryCreate, TaskHistoryUpdate, TaskHistoryResponse, TaskHistoryQuery, TaskHistoryListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_taskhistory(
    taskhistory_data: TaskHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建任务记录
    
    Args:
        taskhistory_data: 任务记录创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的任务记录对象
    """
    service = TaskHistoryService(db)
    return await service.create_taskhistory(taskhistory_data, current_user)


@router.get("/", response_model=dict)
async def get_taskhistories(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    task_id: str = Query(None, description="任务ID"),
    record_status: str = Query(None, description="任务状态"),
    record_batch: int = Query(None, description="任务批次号"),
    start_time_from: str = Query(None, description="开始时间范围-起始（格式：YYYY-MM-DDTHH:MM:SS）"),
    start_time_to: str = Query(None, description="开始时间范围-结束（格式：YYYY-MM-DDTHH:MM:SS）"),
    end_time_from: str = Query(None, description="结束时间范围-起始（格式：YYYY-MM-DDTHH:MM:SS）"),
    end_time_to: str = Query(None, description="结束时间范围-结束（格式：YYYY-MM-DDTHH:MM:SS）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取任务记录列表
    
    Args:
        page: 页码
        size: 每页数量
        task_id: 任务ID
        record_status: 任务状态
        record_batch: 任务批次号
        start_time_from: 开始时间范围-起始
        start_time_to: 开始时间范围-结束
        end_time_from: 结束时间范围-起始
        end_time_to: 结束时间范围-结束
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务记录列表
    """
    service = TaskHistoryService(db)
    return await service.get_taskhistories(
        current_user, page, size, task_id, record_status, record_batch,
        start_time_from, start_time_to, end_time_from, end_time_to
    )


@router.get("/{taskhistory_id}", response_model=dict)
async def get_taskhistory_by_id(
    taskhistory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取任务记录
    
    Args:
        taskhistory_id: 任务记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        任务记录对象
    """
    service = TaskHistoryService(db)
    return await service.get_taskhistory_by_id(taskhistory_id, current_user)


@router.put("/{taskhistory_id}", response_model=dict)
async def update_taskhistory(
    taskhistory_id: str,
    taskhistory_data: TaskHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新任务记录
    
    Args:
        taskhistory_id: 任务记录ID
        taskhistory_data: 任务记录更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的任务记录对象
    """
    service = TaskHistoryService(db)
    return await service.update_taskhistory(taskhistory_id, taskhistory_data, current_user)


@router.delete("/{taskhistory_id}", response_model=dict)
async def delete_taskhistory(
    taskhistory_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除任务记录
    
    Args:
        taskhistory_id: 任务记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = TaskHistoryService(db)
    return await service.delete_taskhistory(taskhistory_id, current_user)


@router.get("/stats/overview", response_model=dict)
async def get_taskhistory_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取任务记录统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        统计信息
    """
    service = TaskHistoryService(db)
    return await service.get_taskhistory_stats(current_user)