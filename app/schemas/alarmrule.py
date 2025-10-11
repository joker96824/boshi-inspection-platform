"""
报警规则数据验证模式
"""

from typing import Optional, Dict, Any, List
from pydantic import Field
from .base import BaseSchema, BaseResponse


class AlarmRuleBase(BaseSchema):
    """报警规则基础模式"""
    rule_name: str = Field(..., min_length=1, max_length=100, description="规则名称")
    item_id: str = Field(..., description="巡检项目ID")
    alarm_param: Optional[Dict[str, Any]] = Field(None, description="报警参数")


class AlarmRuleCreate(AlarmRuleBase):
    """报警规则创建模式"""
    pass


class AlarmRuleUpdate(BaseSchema):
    """报警规则更新模式"""
    rule_name: Optional[str] = Field(None, min_length=1, max_length=100, description="规则名称")
    item_id: Optional[str] = Field(None, description="巡检项目ID")
    alarm_param: Optional[Dict[str, Any]] = Field(None, description="报警参数")


class AlarmRuleResponse(BaseResponse):
    """报警规则响应模式"""
    id: str = Field(..., description="报警规则ID")
    rule_name: str = Field(..., description="规则名称")
    item_id: str = Field(..., description="巡检项目ID")
    alarm_param: Optional[Dict[str, Any]] = Field(None, description="报警参数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class AlarmRuleQuery(BaseSchema):
    """报警规则查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    rule_name: Optional[str] = Field(None, description="规则名称（模糊匹配）")
    item_id: Optional[str] = Field(None, description="巡检项目ID")


class AlarmRuleListResponse(BaseSchema):
    """报警规则列表响应模式"""
    items: List[AlarmRuleResponse] = Field(..., description="报警规则列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

