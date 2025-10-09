"""
地图路网数据验证模型
"""

from typing import Optional, Dict, Any
from enum import Enum
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class MapNetType(str, Enum):
    """地图路网元素类型枚举"""
    POINT = "point"
    LINE = "line"
    RECT = "rect"


class MapNetBase(BaseSchema):
    """地图路网基础模式"""
    map_net_type: MapNetType = Field(..., description="元素类型（point/line/rect）")
    map_net_properties: Optional[Dict[str, Any]] = Field(None, description="路网元素属性")
    map_net_geometry: Optional[Dict[str, Any]] = Field(None, description="路网元素地理信息")

    @validator('map_net_properties')
    def validate_map_net_properties(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("路网元素属性必须是有效的JSON对象")
        return v

    @validator('map_net_geometry')
    def validate_map_net_geometry(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("路网元素地理信息必须是有效的JSON对象")
        return v


class MapNetCreate(MapNetBase):
    """创建地图路网请求模式"""
    map_id: str = Field(..., description="所属地图ID")


class MapNetUpdate(BaseSchema):
    """更新地图路网请求模式"""
    map_net_type: Optional[MapNetType] = Field(None, description="元素类型（point/line/rect）")
    map_net_properties: Optional[Dict[str, Any]] = Field(None, description="路网元素属性")
    map_net_geometry: Optional[Dict[str, Any]] = Field(None, description="路网元素地理信息")

    @validator('map_net_properties')
    def validate_map_net_properties(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("路网元素属性必须是有效的JSON对象")
        return v

    @validator('map_net_geometry')
    def validate_map_net_geometry(cls, v):
        if v is not None and not isinstance(v, dict):
            raise ValueError("路网元素地理信息必须是有效的JSON对象")
        return v


class MapNetResponse(MapNetBase, BaseResponse):
    """地图路网响应模式"""
    map_id: str = Field(..., description="所属地图ID")

    class Config:
        from_attributes = True


class MapNetQuery(BaseSchema):
    """地图路网查询模式"""
    map_id: str = Field(..., description="地图ID")
    map_net_type: Optional[str] = Field(None, description="元素类型（模糊匹配）")
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")


class MapNetListResponse(BaseSchema):
    """地图路网列表响应模式"""
    items: list[MapNetResponse] = Field(..., description="路网元素列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
