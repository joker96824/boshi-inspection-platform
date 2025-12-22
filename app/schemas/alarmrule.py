"""
报警规则数据验证模式
"""

from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class RelationItem(BaseSchema):
    """关联对象项"""
    type: str = Field(..., description="关联类型：item, gimbal, sensor, robot")
    id: str = Field(..., description="关联对象ID")
    sort_order: int = Field(0, description="顺序，用于多数据源规则")

    @validator('type')
    def validate_type(cls, v):
        if v not in ['item', 'gimbal', 'sensor', 'robot']:
            raise ValueError('关联类型必须是 item, gimbal, sensor 或 robot')
        return v


class AlarmRuleBase(BaseSchema):
    """报警规则基础模式"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    alarm_category: str = Field(..., description="报警分类：robot, inspection, gimbal, sensor, other")
    alarm_level: int = Field(..., ge=1, le=10, description="报警等级 1-10")
    rule_type: str = Field(..., description="规则类型：value_range, bool_value, sum_value, diff_value, avg_range, complex")
    rule_config: Optional[Dict[str, Any]] = Field(None, description="规则配置（JSON格式）")
    enabled: bool = Field(True, description="是否启用")
    description: Optional[str] = Field(None, description="规则描述")
    is_global: bool = Field(False, description="是否全局规则")

    @validator('alarm_category')
    def validate_category(cls, v):
        if v not in ['robot', 'inspection', 'gimbal', 'sensor', 'other']:
            raise ValueError('报警分类必须是 robot, inspection, gimbal, sensor 或 other')
        return v

    @validator('rule_type')
    def validate_rule_type(cls, v):
        if v not in ['value_range', 'bool_value', 'sum_value', 'diff_value', 'avg_range', 'complex']:
            raise ValueError('规则类型必须是 value_range, bool_value, sum_value, diff_value, avg_range 或 complex')
        return v


class AlarmRuleCreate(AlarmRuleBase):
    """报警规则创建模式"""
    relations: Optional[List[RelationItem]] = Field(default=[], description="关联对象列表")

    @validator('relations')
    def validate_relations(cls, v, values):
        is_global = values.get('is_global', False)
        if is_global and v:
            raise ValueError('全局规则不能关联对象')
        if not is_global and not v:
            raise ValueError('非全局规则必须至少关联一个对象')
        return v


class AlarmRuleUpdate(BaseSchema):
    """报警规则更新模式"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100, description="规则名称")
    alarm_category: Optional[str] = Field(None, description="报警分类")
    alarm_level: Optional[int] = Field(None, ge=1, le=10, description="报警等级 1-10")
    rule_type: Optional[str] = Field(None, description="规则类型")
    rule_config: Optional[Dict[str, Any]] = Field(None, description="规则配置（JSON格式）")
    enabled: Optional[bool] = Field(None, description="是否启用")
    description: Optional[str] = Field(None, description="规则描述")
    is_global: Optional[bool] = Field(None, description="是否全局规则")

    @validator('alarm_category')
    def validate_category(cls, v):
        if v and v not in ['robot', 'inspection', 'gimbal', 'sensor', 'other']:
            raise ValueError('报警分类必须是 robot, inspection, gimbal, sensor 或 other')
        return v

    @validator('rule_type')
    def validate_rule_type(cls, v):
        if v and v not in ['value_range', 'bool_value', 'sum_value', 'diff_value', 'avg_range', 'complex']:
            raise ValueError('规则类型必须是 value_range, bool_value, sum_value, diff_value, avg_range 或 complex')
        return v


class AlarmRuleResponse(BaseResponse):
    """报警规则响应模式"""
    id: str = Field(..., description="报警规则ID")
    rule_name: str = Field(..., description="规则名称")
    alarm_category: str = Field(..., description="报警分类")
    alarm_level: int = Field(..., description="报警等级")
    rule_type: str = Field(..., description="规则类型")
    rule_config: Optional[Dict[str, Any]] = Field(None, description="规则配置")
    enabled: bool = Field(..., description="是否启用")
    description: Optional[str] = Field(None, description="规则描述")
    is_global: bool = Field(..., description="是否全局规则")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")
    relations: Optional[List[Dict[str, Any]]] = Field(None, description="关联对象列表")


class AlarmRuleQuery(BaseSchema):
    """报警规则查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    rule_name: Optional[str] = Field(None, description="规则名称（模糊匹配）")
    alarm_category: Optional[str] = Field(None, description="报警分类")
    alarm_level: Optional[int] = Field(None, description="报警等级")
    rule_type: Optional[str] = Field(None, description="规则类型")
    enabled: Optional[bool] = Field(None, description="是否启用")
    is_global: Optional[bool] = Field(None, description="是否全局规则")


class AlarmRuleListResponse(BaseSchema):
    """报警规则列表响应模式"""
    items: List[AlarmRuleResponse] = Field(..., description="报警规则列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
