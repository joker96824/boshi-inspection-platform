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


class PointCreate(PointBase):
    """巡检点创建模式"""
    pass


class PointUpdate(BaseSchema):
    """巡检点更新模式"""
    point_name: Optional[str] = Field(None, min_length=1, max_length=100, description="巡检点名称")
    point_actions: Optional[Dict[str, Any]] = Field(None, description="巡检点动作")


class PointResponse(BaseResponse):
    """巡检点响应模式"""
    point_name: str = Field(..., description="巡检点名称")
    map_id: str = Field(..., description="所属地图ID")
    point_actions: Optional[Dict[str, Any]] = Field(None, description="巡检点动作")


class PointQuery(BaseSchema):
    """巡检点查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    point_name: Optional[str] = Field(None, description="巡检点名称（模糊匹配）")


class PointListResponse(BaseSchema):
    """巡检点列表响应模式"""
    items: List[PointResponse] = Field(..., description="巡检点列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
