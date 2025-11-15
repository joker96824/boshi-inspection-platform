"""
巡检点相关模式
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class PointBase(BaseSchema):
    """巡检点基础模式"""
    point_name: str = Field(..., min_length=1, max_length=100, description="巡检点名称")
    map_id: str = Field(..., description="所属地图ID")
    point_actions: Optional[Dict[str, Any]] = Field(None, description="巡检点动作")
    x_coordinate: float = Field(..., description="X坐标（地图横坐标）")
    y_coordinate: float = Field(..., description="Y坐标（地图纵坐标）")


class PointCreate(PointBase):
    """巡检点创建模式"""
    pass


class PointUpdate(BaseSchema):
    """巡检点更新模式"""
    point_name: Optional[str] = Field(None, min_length=1, max_length=100, description="巡检点名称")
    point_actions: Optional[Dict[str, Any]] = Field(None, description="巡检点动作")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")


class PointResponse(BaseResponse):
    """巡检点响应模式"""
    point_name: str = Field(..., description="巡检点名称")
    map_id: str = Field(..., description="所属地图ID")
    point_actions: Optional[Dict[str, Any]] = Field(None, description="巡检点动作")
    x_coordinate: Optional[float] = Field(None, description="X坐标（地图横坐标）")
    y_coordinate: Optional[float] = Field(None, description="Y坐标（地图纵坐标）")


class PointQuery(BaseSchema):
    """巡检点查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    point_name: Optional[str] = Field(None, description="巡检点名称（模糊匹配）")


class PointListResponse(BaseSchema):
    """巡检点列表响应模式"""
    items: List[PointResponse] = Field(..., description="巡检点列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
