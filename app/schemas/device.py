"""
设备Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class DeviceBase(BaseSchema):
    """设备基础模式"""
    device_name: str = Field(..., min_length=1, max_length=100, description="设备名称")
    device_params: Optional[Dict[str, Any]] = Field(None, description="设备参数")
    point_id: str = Field(..., description="所属巡检点ID")
    enabled: bool = Field(True, description="启用状态：True-启用，False-禁用")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")


class DeviceCreate(DeviceBase):
    """设备创建模式"""
    pass


class DeviceUpdate(BaseSchema):
    """设备更新模式"""
    device_name: Optional[str] = Field(None, min_length=1, max_length=100, description="设备名称")
    device_params: Optional[Dict[str, Any]] = Field(None, description="设备参数")
    point_id: Optional[str] = Field(None, description="所属巡检点ID")
    enabled: Optional[bool] = Field(None, description="启用状态：True-启用，False-禁用")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")


class DeviceResponse(BaseResponse):
    """设备响应模式"""
    id: str = Field(..., description="设备ID")
    device_name: str = Field(..., description="设备名称")
    device_params: Optional[Dict[str, Any]] = Field(None, description="设备参数")
    point_id: str = Field(..., description="所属巡检点ID")
    enabled: bool = Field(..., description="启用状态：True-启用，False-禁用")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class DeviceQuery(BaseSchema):
    """设备查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    device_name: Optional[str] = Field(None, description="设备名称（模糊查询）")
    point_id: Optional[str] = Field(None, description="巡检点ID筛选")


class DeviceListResponse(BaseSchema):
    """设备列表响应模式"""
    items: List[DeviceResponse] = Field(..., description="设备列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

