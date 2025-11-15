"""
地图数据验证模型
"""

from typing import Optional
from decimal import Decimal
from pydantic import Field, validator
from .base import BaseSchema, BaseResponse


class MapBase(BaseSchema):
    """地图基础模式"""
    map_name: str = Field(..., min_length=1, max_length=100, description="地图名称")
    map_image_url: Optional[str] = Field(None, max_length=500, description="图片地址")
    map_scale: Optional[Decimal] = Field(None, ge=0, description="比例尺")
    map_center_x: Optional[Decimal] = Field(None, description="中心点横坐标")
    map_center_y: Optional[Decimal] = Field(None, description="中心点纵坐标")
    factory_id: Optional[str] = Field(None, description="厂区ID")

    @validator('map_name')
    def validate_map_name(cls, v):
        if not v or not v.strip():
            raise ValueError("地图名称不能为空")
        return v.strip()

    @validator('map_image_url')
    def validate_map_image_url(cls, v):
        if v is not None and v.strip():
            v = v.strip()
            # 简单的URL格式验证
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
                raise ValueError("图片地址格式不正确")
            return v
        return None


class MapCreate(MapBase):
    """创建地图请求模式"""
    pass


class MapUpdate(BaseSchema):
    """更新地图请求模式"""
    map_name: Optional[str] = Field(None, min_length=1, max_length=100, description="地图名称")
    map_image_url: Optional[str] = Field(None, max_length=500, description="图片地址")
    map_scale: Optional[Decimal] = Field(None, ge=0, description="比例尺")
    map_center_x: Optional[Decimal] = Field(None, description="中心点横坐标")
    map_center_y: Optional[Decimal] = Field(None, description="中心点纵坐标")
    factory_id: Optional[str] = Field(None, description="厂区ID")

    @validator('map_name')
    def validate_map_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("地图名称不能为空")
        return v.strip() if v else None

    @validator('map_image_url')
    def validate_map_image_url(cls, v):
        if v is not None and v.strip():
            v = v.strip()
            # 简单的URL格式验证
            if not (v.startswith('http://') or v.startswith('https://') or v.startswith('/')):
                raise ValueError("图片地址格式不正确")
            return v
        return None


class MapResponse(MapBase, BaseResponse):
    """地图响应模式"""
    user_id: str = Field(..., description="所属用户ID")

    class Config:
        from_attributes = True


class MapQuery(BaseSchema):
    """地图查询模式"""
    map_name: Optional[str] = Field(None, description="地图名称（模糊匹配）")
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")


class MapListResponse(BaseSchema):
    """地图列表响应模式"""
    items: list[MapResponse] = Field(..., description="地图列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
