"""
报警规则API路由
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_read_permission
from ...services.alarmrule_service import AlarmRuleService
from ...schemas.alarmrule import (
    AlarmRuleCreate, AlarmRuleUpdate, AlarmRuleQuery,
    AlarmRuleResponse, AlarmRuleListResponse
)

router = APIRouter()


@router.post("/", response_model=dict)
async def create_alarmrule(
    alarmrule_data: AlarmRuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """创建报警规则
    
    Args:
        alarmrule_data: 报警规则创建数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        创建的报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.create_alarmrule(alarmrule_data, current_user)


@router.get("/by-ids", response_model=dict)
async def get_alarmrules_by_ids(
    alarmrule_ids: List[str] = Query(..., description="报警规则ID列表（支持单个或多个ID查询）"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID列表查询报警规则
    
    支持单个或多个ID查询
    
    Args:
        alarmrule_ids: 报警规则ID列表
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        报警规则列表
    """
    service = AlarmRuleService(db)
    return await service.get_alarmrules_by_ids(alarmrule_ids, current_user)


@router.get("/", response_model=dict)
async def get_alarmrules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页数量"),
    rule_name: Optional[str] = Query(None, description="规则名称（模糊匹配）"),
    item_id: Optional[str] = Query(None, description="巡检项目ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """分页查询报警规则列表
    
    Args:
        page: 页码
        size: 每页数量
        rule_name: 规则名称（模糊匹配）
        item_id: 巡检项目ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分页的报警规则列表
    """
    query = AlarmRuleQuery(page=page, size=size, rule_name=rule_name, item_id=item_id)
    service = AlarmRuleService(db)
    return await service.get_alarmrules(query, current_user)


@router.get("/{alarmrule_id}", response_model=dict)
async def get_alarmrule_by_id(
    alarmrule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """根据ID获取报警规则
    
    Args:
        alarmrule_id: 报警规则ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.get_alarmrule_by_id(alarmrule_id, current_user)


@router.put("/{alarmrule_id}", response_model=dict)
async def update_alarmrule(
    alarmrule_id: str,
    alarmrule_data: AlarmRuleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """更新报警规则
    
    Args:
        alarmrule_id: 报警规则ID
        alarmrule_data: 更新数据
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.update_alarmrule(alarmrule_id, alarmrule_data, current_user)


@router.delete("/{alarmrule_id}", response_model=dict)
async def delete_alarmrule(
    alarmrule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除报警规则（软删除）
    
    Args:
        alarmrule_id: 报警规则ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        删除结果
    """
    service = AlarmRuleService(db)
    return await service.delete_alarmrule(alarmrule_id, current_user)


@router.get("/stats/summary", response_model=dict)
async def get_alarmrule_stats(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_read_permission)
):
    """获取报警规则统计信息
    
    Args:
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        统计信息
    """
    service = AlarmRuleService(db)
    return await service.get_alarmrule_stats(current_user)

