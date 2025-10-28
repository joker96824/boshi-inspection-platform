"""
云台日程Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GimbalScheduleBase(BaseSchema):
    """云台日程基础模式"""
    schedule_type: str = Field(..., min_length=1, max_length=50, description="云台日程类型")
    schedule_is_active: bool = Field(True, description="云台日程是否激活")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")


class GimbalScheduleCreate(GimbalScheduleBase):
    """云台日程创建模式"""
    pass


class GimbalScheduleUpdate(BaseSchema):
    """云台日程更新模式"""
    schedule_type: Optional[str] = Field(None, min_length=1, max_length=50, description="云台日程类型")
    schedule_is_active: Optional[bool] = Field(None, description="云台日程是否激活")
    gimbaltask_id: Optional[str] = Field(None, description="关联云台任务ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: Optional[int] = Field(None, description="设置时间（Unix时间戳）")


class GimbalScheduleResponse(BaseResponse):
    """云台日程响应模式"""
    id: str = Field(..., description="云台日程ID")
    schedule_type: str = Field(..., description="云台日程类型")
    schedule_is_active: bool = Field(..., description="云台日程是否激活")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalScheduleQuery(BaseSchema):
    """云台日程查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    schedule_type: Optional[str] = Field(None, description="云台日程类型筛选")
    schedule_is_active: Optional[bool] = Field(None, description="激活状态筛选")
    gimbaltask_id: Optional[str] = Field(None, description="云台任务ID筛选")


class GimbalScheduleListResponse(BaseSchema):
    """云台日程列表响应模式"""
    items: List[GimbalScheduleResponse] = Field(..., description="云台日程列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
