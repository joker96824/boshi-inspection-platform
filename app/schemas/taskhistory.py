"""
任务记录Pydantic模式
"""

from typing import Optional, List
from pydantic import Field, validator
from datetime import datetime
from .base import BaseSchema, BaseResponse
from ..core.task_status import TaskStatus


class TaskHistoryBase(BaseSchema):
    """任务记录基础模式"""
    task_id: str = Field(..., description="关联任务ID")
    record_start_time: str = Field(..., min_length=1, max_length=50, description="任务开始时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_end_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务结束时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_status: str = Field(..., description="任务状态：running-执行中, paused-已暂停, completed-已完成, failed-执行失败, cancelled-已取消")
    record_batch: int = Field(..., ge=1, description="任务批次号")
    current_point_id: Optional[str] = Field(None, description="当前执行的巡检点ID")
    current_item_id: Optional[str] = Field(None, description="当前执行的巡检项目ID")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('record_start_time')
    def validate_start_time(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式必须为 YYYY-MM-DDTHH:MM:SS')
        return v
    
    @validator('record_end_time')
    def validate_end_time(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式必须为 YYYY-MM-DDTHH:MM:SS')
        return v
    
    @validator('record_status')
    def validate_record_status(cls, v):
        """验证任务状态值"""
        if not TaskStatus.is_valid(v):
            valid_statuses = ", ".join(TaskStatus.get_all_statuses())
            raise ValueError(f"任务状态必须是以下值之一: {valid_statuses}")
        return v
    
    @validator('view_status')
    def validate_view_status(cls, v):
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


class TaskHistoryCreate(TaskHistoryBase):
    """任务记录创建模式"""
    pass


class TaskHistoryUpdate(BaseSchema):
    """任务记录更新模式"""
    record_start_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务开始时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_end_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务结束时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_status: Optional[str] = Field(None, description="任务状态：running-执行中, paused-已暂停, completed-已完成, failed-执行失败, cancelled-已取消")
    record_batch: Optional[int] = Field(None, ge=1, description="任务批次号")
    current_point_id: Optional[str] = Field(None, description="当前执行的巡检点ID")
    current_item_id: Optional[str] = Field(None, description="当前执行的巡检项目ID")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    
    @validator('record_start_time')
    def validate_start_time(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式必须为 YYYY-MM-DDTHH:MM:SS')
        return v
    
    @validator('record_end_time')
    def validate_end_time(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式必须为 YYYY-MM-DDTHH:MM:SS')
        return v
    
    @validator('record_status')
    def validate_record_status(cls, v):
        """验证任务状态值"""
        if v is not None and not TaskStatus.is_valid(v):
            valid_statuses = ", ".join(TaskStatus.get_all_statuses())
            raise ValueError(f"任务状态必须是以下值之一: {valid_statuses}")
        return v
    
    @validator('view_status')
    def validate_view_status(cls, v):
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


class TaskHistoryResponse(BaseResponse):
    """任务记录响应模式"""
    task_id: str = Field(..., description="关联任务ID")
    record_start_time: str = Field(..., description="任务开始时间")
    record_end_time: Optional[str] = Field(None, description="任务结束时间")
    record_status: str = Field(..., description="任务状态")
    record_status_display: str = Field(..., description="任务状态显示文本")
    record_batch: int = Field(..., description="任务批次号")
    current_point_id: Optional[str] = Field(None, description="当前执行的巡检点ID")
    current_item_id: Optional[str] = Field(None, description="当前执行的巡检项目ID")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理（有报警信息时使用，无异常时为空）")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")


class TaskHistoryQuery(BaseSchema):
    """任务记录查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    task_id: Optional[str] = Field(None, description="任务信息ID")
    record_status: Optional[str] = Field(None, description="任务状态")
    record_batch: Optional[int] = Field(None, description="任务批次号")
    view_status: Optional[str] = Field(None, description="查看状态：pending-未查看, viewed-已查看, processed-已处理")
    inspection_result_status: Optional[str] = Field(None, description="巡检结果状态：null-尚未结束（任务进行中）, normal-正常（任务完成且无异常）, warning-预警报警, critical-严重报警, emergency-危机报警")
    start_time_from: Optional[str] = Field(None, description="开始时间范围-起始（格式：YYYY-MM-DDTHH:MM:SS）")
    start_time_to: Optional[str] = Field(None, description="开始时间范围-结束（格式：YYYY-MM-DDTHH:MM:SS）")
    end_time_from: Optional[str] = Field(None, description="结束时间范围-起始（格式：YYYY-MM-DDTHH:MM:SS）")
    end_time_to: Optional[str] = Field(None, description="结束时间范围-结束（格式：YYYY-MM-DDTHH:MM:SS）")
    
    @validator('start_time_from', 'start_time_to', 'end_time_from', 'end_time_to')
    def validate_time_format(cls, v):
        if v:
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式必须为 YYYY-MM-DDTHH:MM:SS')
        return v
    
    @validator('view_status')
    def validate_view_status(cls, v):
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


class TaskHistoryListResponse(BaseSchema):
    """任务记录列表响应模式"""
    items: List[TaskHistoryResponse] = Field(..., description="任务记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
