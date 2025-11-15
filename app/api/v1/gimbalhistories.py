"""
云台巡检记录API路由
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from ...core.deps import get_db, validate_pagination_params
from ...core.permissions import require_no_auth, require_write_permission
from ...schemas.gimbalhistory import (
    GimbalHistoryCreate,
    GimbalHistoryQuery,
    GimbalHistoryUpdate,
)
from ...services.gimbalhistory_service import GimbalHistoryService

router = APIRouter()


@router.post("/", response_model=dict)
async def create_gimbal_history(
    history_data: GimbalHistoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """创建云台巡检记录"""
    service = GimbalHistoryService(db)
    return await service.create_gimbal_history(history_data, current_user)


@router.get("/", response_model=dict)
async def get_gimbal_histories(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    inspection_project_id: Optional[str] = Query(
        None, description="云台巡检项目ID筛选"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台巡检记录列表"""
    query = GimbalHistoryQuery(
        page=page,
        size=size,
        inspection_project_id=inspection_project_id,
    )
    service = GimbalHistoryService(db)
    return await service.get_gimbal_histories(query, current_user)


@router.get("/by-ids", response_model=dict)
async def get_gimbal_histories_by_ids(
    gimbalhistory_ids: List[str] = Query(
        ..., description="云台巡检记录ID列表（支持单个或多个ID查询）"
    ),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID列表查询云台巡检记录"""
    service = GimbalHistoryService(db)
    return await service.get_gimbal_histories_by_ids(gimbalhistory_ids, current_user)


@router.get("/{history_id}", response_model=dict)
async def get_gimbal_history_by_id(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """根据ID获取云台巡检记录详情"""
    service = GimbalHistoryService(db)
    return await service.get_gimbal_history_by_id(history_id, current_user)


@router.put("/{history_id}", response_model=dict)
async def update_gimbal_history(
    history_id: str,
    history_data: GimbalHistoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """更新云台巡检记录"""
    service = GimbalHistoryService(db)
    return await service.update_gimbal_history(history_id, history_data, current_user)


@router.delete("/{history_id}", response_model=dict)
async def delete_gimbal_history(
    history_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission),
):
    """删除云台巡检记录"""
    service = GimbalHistoryService(db)
    return await service.delete_gimbal_history(history_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_gimbal_history_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth()),
):
    """获取云台巡检记录统计信息"""
    service = GimbalHistoryService(db)
    return await service.get_gimbal_history_stats(current_user)
