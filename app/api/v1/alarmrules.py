"""
报警规则API路由
"""

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any

from ...core.deps import get_db
from ...core.permissions import require_write_permission, require_no_auth
from ...services.alarmrule_service import AlarmRuleService
from ...schemas.alarmrule import AlarmRuleCreate, AlarmRuleUpdate, AlarmRuleQuery

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


@router.get("/", response_model=dict)
async def get_alarmrules(
    page: Optional[int] = Query(None, gt=0, description="页码（可选，大于0，必须与size同时提供）"),
    size: Optional[int] = Query(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）"),
    rule_name: Optional[str] = Query(None, description="规则名称（模糊匹配）"),
    alarm_category: Optional[str] = Query(None, description="报警分类"),
    alarm_level: Optional[int] = Query(None, description="报警等级"),
    rule_type: Optional[str] = Query(None, description="规则类型"),
    enabled: Optional[bool] = Query(None, description="是否启用"),
    is_global: Optional[bool] = Query(None, description="是否全局规则"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """分页查询报警规则列表
    
    Args:
        page: 页码
        size: 每页数量
        rule_name: 规则名称（模糊匹配）
        alarm_category: 报警分类
        alarm_level: 报警等级
        rule_type: 规则类型
        enabled: 是否启用
        is_global: 是否全局规则
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        分页的报警规则列表
    """
    query = AlarmRuleQuery(
        page=page,
        size=size,
        rule_name=rule_name,
        alarm_category=alarm_category,
        alarm_level=alarm_level,
        rule_type=rule_type,
        enabled=enabled,
        is_global=is_global
    )
    service = AlarmRuleService(db)
    return await service.get_alarmrules(query, current_user)


@router.get("/{alarmrule_id}", response_model=dict)
async def get_alarmrule_by_id(
    alarmrule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
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


@router.put("/{alarmrule_id}/enable", response_model=dict)
async def enable_alarmrule(
    alarmrule_id: str,
    enabled: bool = Body(..., description="是否启用"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """启用/禁用报警规则
    
    Args:
        alarmrule_id: 报警规则ID
        enabled: 是否启用
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.enable_alarmrule(alarmrule_id, enabled, current_user)


@router.get("/{alarmrule_id}/relations", response_model=dict)
async def get_alarmrule_relations(
    alarmrule_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[dict] = Depends(require_no_auth())
):
    """获取报警规则的关联对象列表
    
    Args:
        alarmrule_id: 报警规则ID
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        关联对象列表
    """
    service = AlarmRuleService(db)
    return await service.get_relations(alarmrule_id, current_user)


@router.post("/{alarmrule_id}/relations", response_model=dict)
async def add_alarmrule_relations(
    alarmrule_id: str,
    relations: List[Dict[str, Any]] = Body(..., description="关联对象列表"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """为报警规则添加关联对象
    
    Args:
        alarmrule_id: 报警规则ID
        relations: 关联对象列表，格式：[{"type": "item", "id": "xxx", "sort_order": 1}]
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.add_relations(alarmrule_id, relations, current_user)


@router.delete("/{alarmrule_id}/relations", response_model=dict)
async def remove_alarmrule_relations(
    alarmrule_id: str,
    relations: List[Dict[str, Any]] = Body(..., description="关联对象列表"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(require_write_permission)
):
    """删除报警规则的关联对象
    
    Args:
        alarmrule_id: 报警规则ID
        relations: 关联对象列表，格式：[{"type": "item", "id": "xxx"}]
        db: 数据库会话
        current_user: 当前用户
    
    Returns:
        更新后的报警规则对象
    """
    service = AlarmRuleService(db)
    return await service.remove_relations(alarmrule_id, relations, current_user)
