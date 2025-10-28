"""
云台记录API路由
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.gimbalhistory_service import GimbalHistoryService
from ...schemas.gimbalhistory import GimbalHistoryCreate, GimbalHistoryUpdate, GimbalHistoryResponse, GimbalHistoryQuery, GimbalHistoryListResponse
from ...utils.response import ApiResponse

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal_history(
    history_data: GimbalHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建云台记录
    
    Args:
        history_data: 云台记录创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的云台记录信息
    """
    service = GimbalHistoryService(db)
    return await service.create_gimbal_history(history_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbal_histories(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    gimbaltask_id: Optional[str] = Query(None, description="云台任务ID筛选"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台记录列表
    
    Args:
        page: 页码
        size: 每页数量
        gimbaltask_id: 云台任务ID筛选
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台记录列表和分页信息
    """
    query = GimbalHistoryQuery(
        page=page,
        size=size,
        gimbaltask_id=gimbaltask_id
    )
    service = GimbalHistoryService(db)
    return await service.get_gimbal_histories(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbal_histories_by_ids(
    gimbalhistory_ids: List[str] = Query(..., description="云台记录ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID列表查询云台记录
    
    支持单个或多个ID查询
    
    Args:
        gimbalhistory_ids: 云台记录ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台记录列表
    """
    service = GimbalHistoryService(db)
    return await service.get_gimbal_histories_by_ids(gimbalhistory_ids, current_user)


@router.get("/{history_id}", response_model=dict)
async def get_gimbal_history_by_id(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """根据ID获取云台记录详情
    
    Args:
        history_id: 云台记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台记录详情
    """
    service = GimbalHistoryService(db)
    return await service.get_gimbal_history_by_id(history_id, current_user)


@router.put("/{history_id}", response_model=dict)
async def update_gimbal_history(
    history_id: str,
    history_data: GimbalHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新云台记录
    
    Args:
        history_id: 云台记录ID
        history_data: 云台记录更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的云台记录信息
    """
    service = GimbalHistoryService(db)
    return await service.update_gimbal_history(history_id, history_data, current_user)


@router.delete("/{history_id}", response_model=dict)
async def delete_gimbal_history(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除云台记录
    
    Args:
        history_id: 云台记录ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = GimbalHistoryService(db)
    return await service.delete_gimbal_history(history_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_history_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取云台记录统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        云台记录统计信息
    """
    service = GimbalHistoryService(db)
    return await service.get_gimbal_history_stats(current_user)
