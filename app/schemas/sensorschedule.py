"""
传感器日程Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class SensorScheduleBase(BaseSchema):
    """传感器日程基础模式"""
    schedule_type: str = Field(..., min_length=1, max_length=50, description="传感器日程类型")
    schedule_is_active: bool = Field(True, description="传感器日程是否激活")
    sensor_id: str = Field(..., description="关联传感器ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")


class SensorScheduleCreate(SensorScheduleBase):
    """传感器日程创建模式"""
    pass


class SensorScheduleUpdate(BaseSchema):
    """传感器日程更新模式"""
    schedule_type: Optional[str] = Field(None, min_length=1, max_length=50, description="传感器日程类型")
    schedule_is_active: Optional[bool] = Field(None, description="传感器日程是否激活")
    sensor_id: Optional[str] = Field(None, description="关联传感器ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: Optional[int] = Field(None, description="设置时间（Unix时间戳）")


class SensorScheduleResponse(BaseResponse):
    """传感器日程响应模式"""
    id: str = Field(..., description="传感器日程ID")
    schedule_type: str = Field(..., description="传感器日程类型")
    schedule_is_active: bool = Field(..., description="传感器日程是否激活")
    sensor_id: str = Field(..., description="关联传感器ID")
    schedule_param: Optional[Dict[str, Any]] = Field(None, description="日程参数")
    set_time: int = Field(..., description="设置时间（Unix时间戳）")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class SensorScheduleQuery(BaseSchema):
    """传感器日程查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    schedule_type: Optional[str] = Field(None, description="传感器日程类型筛选")
    schedule_is_active: Optional[bool] = Field(None, description="激活状态筛选")
    sensor_id: Optional[str] = Field(None, description="传感器ID筛选")


class SensorScheduleListResponse(BaseSchema):
    """传感器日程列表响应模式"""
    items: List[SensorScheduleResponse] = Field(..., description="传感器日程列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
