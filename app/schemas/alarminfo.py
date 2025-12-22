"""
报警信息数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class AlarmInfoBase(BaseSchema):
    """报警信息基础模式"""
    alarm_rule_id: str = Field(..., description="报警规则ID")
    source_type: str = Field(..., description="数据源类型")
    source_ids: List[str] = Field(..., description="数据源ID列表")
    relation_ids: Optional[List[str]] = Field(None, description="关联对象ID列表")
    trigger_item_ids: Optional[List[str]] = Field(None, description="触发源对应的巡检项目ID列表")
    trigger_project_ids: Optional[List[str]] = Field(None, description="触发源对应的云台巡检项目ID列表")
    trigger_data: Optional[Dict[str, Any]] = Field(None, description="触发时的完整数据快照")
    calculated_value: Optional[Dict[str, Any]] = Field(None, description="计算后的值")
    alarm_message: Optional[str] = Field(None, description="报警信息")

    @validator('source_type')
    def validate_source_type(cls, v):
        if v not in ['itemhistory', 'gimbalhistory', 'sensorhistory', 'robot_status']:
            raise ValueError('数据源类型必须是 itemhistory, gimbalhistory, sensorhistory 或 robot_status')
        return v


class AlarmInfoCreate(AlarmInfoBase):
    """报警信息创建模式"""
    pass


class AlarmInfoUpdate(BaseSchema):
    """报警信息更新模式"""
    alarm_status: Optional[str] = Field(None, description="报警状态：unviewed, unprocessed, processed")
    alarm_message: Optional[str] = Field(None, description="报警信息")
    processed_by: Optional[str] = Field(None, description="处理人")
    process_remark: Optional[str] = Field(None, description="处理备注")

    @validator('alarm_status')
    def validate_status(cls, v):
        if v and v not in ['unviewed', 'unprocessed', 'processed']:
            raise ValueError('报警状态必须是 unviewed, unprocessed 或 processed')
        return v


class AlarmInfoResponse(BaseResponse):
    """报警信息响应模式"""
    id: str = Field(..., description="报警信息ID")
    alarm_rule_id: str = Field(..., description="报警规则ID")
    alarm_category: str = Field(..., description="报警分类")
    alarm_level: int = Field(..., description="报警等级")
    alarm_status: str = Field(..., description="报警状态")
    source_type: str = Field(..., description="数据源类型")
    source_ids: List[str] = Field(..., description="数据源ID列表")
    relation_type: Optional[str] = Field(None, description="关联对象类型")
    relation_ids: Optional[List[str]] = Field(None, description="关联对象ID列表")
    trigger_item_ids: Optional[List[str]] = Field(None, description="触发源对应的巡检项目ID列表")
    trigger_project_ids: Optional[List[str]] = Field(None, description="触发源对应的云台巡检项目ID列表")
    trigger_data: Optional[Dict[str, Any]] = Field(None, description="触发时的完整数据快照")
    calculated_value: Optional[Dict[str, Any]] = Field(None, description="计算后的值")
    alarm_message: Optional[str] = Field(None, description="报警信息")
    processed_by: Optional[str] = Field(None, description="处理人")
    processed_at: Optional[str] = Field(None, description="处理时间")
    process_remark: Optional[str] = Field(None, description="处理备注")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class AlarmInfoProcessRequest(BaseSchema):
    """处理报警请求模式"""
    process_remark: str = Field(..., description="处理备注")


class AlarmInfoStatusUpdateRequest(BaseSchema):
    """更新报警状态请求模式"""
    alarm_status: str = Field(..., description="报警状态：unviewed, unprocessed, processed")
    
    @validator('alarm_status')
    def validate_alarm_status(cls, v):
        if v not in ['unviewed', 'unprocessed', 'processed']:
            raise ValueError('报警状态必须是 unviewed, unprocessed 或 processed')
        return v


class AlarmInfoQuery(BaseSchema):
    """报警信息查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    alarm_rule_id: Optional[str] = Field(None, description="报警规则ID")
    alarm_category: Optional[str] = Field(None, description="报警分类")
    alarm_level: Optional[int] = Field(None, description="报警等级")
    alarm_status: Optional[str] = Field(None, description="报警状态")
    source_type: Optional[str] = Field(None, description="数据源类型")
    relation_type: Optional[str] = Field(None, description="关联对象类型")
    relation_id: Optional[str] = Field(None, description="关联对象ID")
    trigger_item_id: Optional[str] = Field(None, description="触发源对应的巡检项目ID")
    trigger_project_id: Optional[str] = Field(None, description="触发源对应的云台巡检项目ID")


class AlarmInfoListResponse(BaseSchema):
    """报警信息列表响应模式"""
    items: List[AlarmInfoResponse] = Field(..., description="报警信息列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
