"""
任务日程Pydantic模式
"""

from typing import Optional, Dict, Any, List
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class TaskScheduleBase(BaseSchema):
    """任务日程基础模式"""
    schedule_type: str = Field(..., min_length=1, max_length=50, description="任务日程类型")
    task_id: str = Field(..., description="关联任务ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")
    cnt: int = Field(1, ge=1, description="需要执行的次数")


class TaskScheduleCreate(TaskScheduleBase):
    """任务日程创建模式"""
    pass


class TaskScheduleUpdate(BaseSchema):
    """任务日程更新模式"""
    schedule_type: Optional[str] = Field(None, min_length=1, max_length=50, description="任务日程类型")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: Optional[int] = Field(None, description="设置时间（Unix时间戳）")
    cnt: Optional[int] = Field(None, ge=1, description="需要执行的次数")


class TaskScheduleResponse(BaseResponse):
    """任务日程响应模式"""
    schedule_type: str = Field(..., description="任务日程类型")
    schedule_is_active: bool = Field(..., description="任务日程是否激活")
    task_id: str = Field(..., description="关联任务ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")
    cnt: int = Field(..., description="需要执行的次数")


class TaskScheduleQuery(BaseSchema):
    """任务日程查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    task_id: Optional[str] = Field(None, description="任务ID")
    schedule_type: Optional[str] = Field(None, description="日程类型（模糊匹配）")


class TaskScheduleListResponse(BaseSchema):
    """任务日程列表响应模式"""
    items: List[TaskScheduleResponse] = Field(..., description="任务日程列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
