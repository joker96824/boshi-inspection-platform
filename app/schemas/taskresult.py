"""
任务结果数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base import BaseSchema, BaseResponse


class TaskResultBase(BaseSchema):
    """任务结果基础模式"""
    taskhistory_id: str = Field(..., description="任务记录ID")
    record_batch: int = Field(..., description="任务批次")
    result_status: Optional[str] = Field(None, description="结果状态：success-成功, failed-失败, partial-部分成功, warning-警告")
    process_status: Optional[str] = Field(None, description="处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败")
    result_point_id: Optional[str] = Field(None, description="任务结束点ID")
    result_item_id: Optional[str] = Field(None, description="任务结束巡检项目ID")
    result_file_url: Optional[str] = Field(None, description="任务结果文件地址")
    result_collect_time: Optional[str] = Field(None, description="结果采集时间(格式: YYYY-MM-DDTHH:MM:SS)")

    @validator('result_status')
    def validate_result_status(cls, v):
        """验证结果状态"""
        if v is not None and v.strip():
            valid_statuses = ['success', 'failed', 'partial', 'warning']
            if v not in valid_statuses:
                raise ValueError(f'结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v

    @validator('process_status')
    def validate_process_status(cls, v):
        """验证处理状态"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'processing', 'processed', 'failed']
            if v not in valid_statuses:
                raise ValueError(f'处理状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v

    @validator('result_file_url')
    def validate_url(cls, v):
        """验证URL格式"""
        if v is not None and v.strip():
            # 简单的URL格式验证：以"/"开头即可
            if not v.startswith('/'):
                raise ValueError('结果文件地址格式不正确，必须以"/"开头')
        return v
    
    @validator('result_collect_time')
    def validate_datetime(cls, v):
        """验证时间格式"""
        if v is not None and v.strip():
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式不正确，应为YYYY-MM-DDTHH:MM:SS')
        return v


class TaskResultCreate(TaskResultBase):
    """任务结果创建模式"""
    pass


class TaskResultUpdate(BaseSchema):
    """任务结果更新模式"""
    taskhistory_id: Optional[str] = Field(None, description="任务记录ID")
    record_batch: Optional[int] = Field(None, description="任务批次")
    result_status: Optional[str] = Field(None, description="结果状态：success-成功, failed-失败, partial-部分成功, warning-警告")
    process_status: Optional[str] = Field(None, description="处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败")
    result_point_id: Optional[str] = Field(None, description="任务结束点ID")
    result_item_id: Optional[str] = Field(None, description="任务结束巡检项目ID")
    result_file_url: Optional[str] = Field(None, description="任务结果文件地址")
    result_collect_time: Optional[str] = Field(None, description="结果采集时间(格式: YYYY-MM-DDTHH:MM:SS)")

    @validator('result_status')
    def validate_result_status(cls, v):
        """验证结果状态"""
        if v is not None and v.strip():
            valid_statuses = ['success', 'failed', 'partial', 'warning']
            if v not in valid_statuses:
                raise ValueError(f'结果状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v

    @validator('process_status')
    def validate_process_status(cls, v):
        """验证处理状态"""
        if v is not None and v.strip():
            valid_statuses = ['pending', 'processing', 'processed', 'failed']
            if v not in valid_statuses:
                raise ValueError(f'处理状态必须是以下值之一: {", ".join(valid_statuses)}')
        return v

    @validator('result_file_url')
    def validate_url(cls, v):
        """验证URL格式"""
        if v is not None and v.strip():
            # 简单的URL格式验证：以"/"开头即可
            if not v.startswith('/'):
                raise ValueError('结果文件地址格式不正确，必须以"/"开头')
        return v
    
    @validator('result_collect_time')
    def validate_datetime(cls, v):
        """验证时间格式"""
        if v is not None and v.strip():
            try:
                datetime.strptime(v, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                raise ValueError('时间格式不正确，应为YYYY-MM-DDTHH:MM:SS')
        return v


class TaskResultResponse(BaseResponse):
    """任务结果响应模式"""
    id: str = Field(..., description="任务结果ID")
    taskhistory_id: str = Field(..., description="任务记录ID")
    record_batch: int = Field(..., description="任务批次")
    result_status: Optional[str] = Field(None, description="结果状态：success-成功, failed-失败, partial-部分成功, warning-警告")
    process_status: Optional[str] = Field(None, description="处理状态：pending-待处理, processing-处理中, processed-已处理, failed-处理失败")
    result_point_id: Optional[str] = Field(None, description="任务结束点ID")
    result_item_id: Optional[str] = Field(None, description="任务结束巡检项目ID")
    result_file_url: Optional[str] = Field(None, description="任务结果文件地址")
    result_collect_time: Optional[str] = Field(None, description="结果采集时间")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class TaskResultQuery(BaseSchema):
    """任务结果查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    taskresult_ids: Optional[List[str]] = Field(None, description="任务结果ID列表（精确查询）")


class TaskResultListResponse(BaseSchema):
    """任务结果列表响应模式"""
    items: List[TaskResultResponse] = Field(..., description="任务结果列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
