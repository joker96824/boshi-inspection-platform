"""
智能传感器Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class SensorBase(BaseSchema):
    """智能传感器基础模式"""
    device_id: str = Field(..., description="关联设备ID")
    sensor_name: str = Field(..., min_length=1, max_length=100, description="传感器名称")
    sensor_params: Optional[Dict[str, Any]] = Field(None, description="传感器参数")
    group_id: Optional[str] = Field(None, description="关联分组ID")
    enabled: bool = Field(True, description="启用状态：True-启用，False-禁用")


class SensorCreate(SensorBase):
    """智能传感器创建模式"""
    pass


class SensorUpdate(BaseSchema):
    """智能传感器更新模式"""
    device_id: Optional[str] = Field(None, description="关联设备ID")
    sensor_name: Optional[str] = Field(None, min_length=1, max_length=100, description="传感器名称")
    sensor_params: Optional[Dict[str, Any]] = Field(None, description="传感器参数")
    group_id: Optional[str] = Field(None, description="关联分组ID")
    enabled: Optional[bool] = Field(None, description="启用状态：True-启用，False-禁用")


class SensorResponse(BaseResponse):
    """智能传感器响应模式"""
    id: str = Field(..., description="传感器ID")
    device_id: str = Field(..., description="关联设备ID")
    sensor_name: str = Field(..., description="传感器名称")
    sensor_params: Optional[Dict[str, Any]] = Field(None, description="传感器参数")
    group_id: Optional[str] = Field(None, description="关联分组ID")
    group: Optional[Dict[str, Any]] = Field(None, description="分组信息（包含id、group_name、group_description）")
    enabled: bool = Field(..., description="启用状态：True-启用，False-禁用")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class SensorQuery(BaseSchema):
    """智能传感器查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    sensor_name: Optional[str] = Field(None, description="传感器名称（模糊查询）")
    device_id: Optional[str] = Field(None, description="设备ID筛选")


class SensorListResponse(BaseSchema):
    """智能传感器列表响应模式"""
    items: List[SensorResponse] = Field(..., description="智能传感器列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")


class SensorBatchUpdateGroup(BaseSchema):
    """智能传感器批量更新分组模式"""
    sensor_ids: List[str] = Field(..., min_items=1, description="传感器ID列表")
    group_id: Optional[str] = Field(None, description="分组ID（为null表示移除分组）")

