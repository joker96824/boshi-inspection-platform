"""
报警信息数据验证模式
"""

from typing import Optional, Dict, Any, List
from pydantic import Field
from .base import BaseSchema, BaseResponse


class AlarmInfoBase(BaseSchema):
    """报警信息基础模式"""
    alarmrule_id: str = Field(..., description="报警规则ID")
    itemhistory_id: str = Field(..., description="巡检记录ID")
    alarm_data: Optional[Dict[str, Any]] = Field(None, description="触发数据")
    alarm_info: Optional[str] = Field(None, description="报警信息")


class AlarmInfoCreate(AlarmInfoBase):
    """报警信息创建模式"""
    pass


class AlarmInfoUpdate(BaseSchema):
    """报警信息更新模式"""
    alarmrule_id: Optional[str] = Field(None, description="报警规则ID")
    itemhistory_id: Optional[str] = Field(None, description="巡检记录ID")
    alarm_data: Optional[Dict[str, Any]] = Field(None, description="触发数据")
    alarm_info: Optional[str] = Field(None, description="报警信息")


class AlarmInfoResponse(BaseResponse):
    """报警信息响应模式"""
    id: str = Field(..., description="报警信息ID")
    alarmrule_id: str = Field(..., description="报警规则ID")
    itemhistory_id: str = Field(..., description="巡检记录ID")
    alarm_data: Optional[Dict[str, Any]] = Field(None, description="触发数据")
    alarm_info: Optional[str] = Field(None, description="报警信息")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class AlarmInfoQuery(BaseSchema):
    """报警信息查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    alarmrule_id: Optional[str] = Field(None, description="报警规则ID")
    itemhistory_id: Optional[str] = Field(None, description="巡检记录ID")


class AlarmInfoListResponse(BaseSchema):
    """报警信息列表响应模式"""
    items: List[AlarmInfoResponse] = Field(..., description="报警信息列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

