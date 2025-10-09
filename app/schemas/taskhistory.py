"""
任务记录Pydantic模式
"""

from typing import Optional, List
from pydantic import Field, validator
from datetime import datetime
from .base import BaseSchema, BaseResponse


class TaskHistoryBase(BaseSchema):
    """任务记录基础模式"""
    task_id: str = Field(..., description="关联任务ID")
    record_start_time: str = Field(..., min_length=1, max_length=50, description="任务开始时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_end_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务结束时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_status: str = Field(..., min_length=1, max_length=20, description="任务状态")
    record_batch: int = Field(..., ge=1, description="任务批次号")
    
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


class TaskHistoryCreate(TaskHistoryBase):
    """任务记录创建模式"""
    pass


class TaskHistoryUpdate(BaseSchema):
    """任务记录更新模式"""
    record_start_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务开始时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_end_time: Optional[str] = Field(None, min_length=1, max_length=50, description="任务结束时间（格式：YYYY-MM-DDTHH:MM:SS）")
    record_status: Optional[str] = Field(None, min_length=1, max_length=20, description="任务状态")
    record_batch: Optional[int] = Field(None, ge=1, description="任务批次号")
    
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


class TaskHistoryResponse(BaseResponse):
    """任务记录响应模式"""
    task_id: str = Field(..., description="关联任务ID")
    record_start_time: str = Field(..., description="任务开始时间")
    record_end_time: Optional[str] = Field(None, description="任务结束时间")
    record_status: str = Field(..., description="任务状态")
    record_batch: int = Field(..., description="任务批次号")


class TaskHistoryQuery(BaseSchema):
    """任务记录查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    task_id: Optional[str] = Field(None, description="任务信息ID")
    record_status: Optional[str] = Field(None, description="任务状态")
    record_batch: Optional[int] = Field(None, description="任务批次号")
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


class TaskHistoryListResponse(BaseSchema):
    """任务记录列表响应模式"""
    items: List[TaskHistoryResponse] = Field(..., description="任务记录列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
