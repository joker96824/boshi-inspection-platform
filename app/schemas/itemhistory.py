"""
巡检记录Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class ItemHistoryBase(BaseSchema):
    """巡检记录基础模式"""
    taskhistory_id: str = Field(..., description="任务记录ID")
    item_id: str = Field(..., description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
    process_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('process_status')
    def validate_process_status(cls, v):
        """验证查看状态值"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'viewed', 'processed']
            if v not in valid_statuses:
                raise ValueError(f'查看状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v
    
    @validator('inspection_result_status')
    def validate_inspection_result_status(cls, v):
        """验证巡检结果状态值"""
        if v is not None and v.strip():
            valid_statuses = ['normal', 'warning', 'critical', 'emergency']
            if v not in valid_statuses:
                raise ValueError(f'巡检结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class ItemHistoryCreate(ItemHistoryBase):
    """巡检记录创建模式"""
    pass


class ItemHistoryUpdate(BaseSchema):
    """巡检记录更新模式"""
    taskhistory_id: Optional[str] = Field(None, description="任务记录ID")
    item_id: Optional[str] = Field(None, description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
    process_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('process_status')
    def validate_process_status(cls, v):
        """验证查看状态值"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'viewed', 'processed']
            if v not in valid_statuses:
                raise ValueError(f'查看状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v
    
    @validator('inspection_result_status')
    def validate_inspection_result_status(cls, v):
        """验证巡检结果状态值"""
        if v is not None and v.strip():
            valid_statuses = ['normal', 'warning', 'critical', 'emergency']
            if v not in valid_statuses:
                raise ValueError(f'巡检结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class ItemHistoryResponse(BaseResponse):
    """巡检记录响应模式"""
    id: str = Field(..., description="巡检记录ID")
    taskhistory_id: str = Field(..., description="任务记录ID")
    item_id: str = Field(..., description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
    process_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class ItemHistoryQuery(BaseSchema):
    """巡检记录查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    taskhistory_id: Optional[str] = Field(None, description="任务记录ID（精确查询）")
    item_id: Optional[str] = Field(None, description="巡检项目ID（精确查询）")
    taskhistory_ids: Optional[List[str]] = Field(None, description="任务记录ID列表（精确查询）")
    item_ids: Optional[List[str]] = Field(None, description="巡检项目ID列表（精确查询）")
    process_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('process_status')
    def validate_process_status(cls, v):
        """验证查看状态值"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'viewed', 'processed']
            if v not in valid_statuses:
                raise ValueError(f'查看状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v
    
    @validator('inspection_result_status')
    def validate_inspection_result_status(cls, v):
        """验证巡检结果状态值"""
        if v is not None and v.strip():
            valid_statuses = ['normal', 'warning', 'critical', 'emergency']
            if v not in valid_statuses:
                raise ValueError(f'巡检结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v


class ItemHistoryListResponse(BaseSchema):
    """巡检记录列表响应模式"""
    items: List[ItemHistoryResponse] = Field(..., description="巡检记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")


class ItemHistoryWithDetails(ItemHistoryResponse):
    """带详情的巡检记录响应模式"""
    task_name: Optional[str] = Field(None, description="任务名称")
    item_name: Optional[str] = Field(None, description="巡检项目名称")
    item_info: Optional[Dict[str, Any]] = Field(None, description="巡检项目信息")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
