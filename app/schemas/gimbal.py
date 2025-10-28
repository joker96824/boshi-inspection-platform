"""
云台Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GimbalBase(BaseSchema):
    """云台基础模式"""
    gimbal_name: str = Field(..., min_length=1, max_length=100, description="云台名称")
    gimbal_params: Optional[Dict[str, Any]] = Field(None, description="云台参数")
    map_id: Optional[str] = Field(None, description="地图ID")


class GimbalCreate(GimbalBase):
    """云台创建模式"""
    pass


class GimbalUpdate(BaseSchema):
    """云台更新模式"""
    gimbal_name: Optional[str] = Field(None, min_length=1, max_length=100, description="云台名称")
    gimbal_params: Optional[Dict[str, Any]] = Field(None, description="云台参数")
    map_id: Optional[str] = Field(None, description="地图ID")


class GimbalResponse(BaseResponse):
    """云台响应模式"""
    id: str = Field(..., description="云台ID")
    gimbal_name: str = Field(..., description="云台名称")
    gimbal_params: Optional[Dict[str, Any]] = Field(None, description="云台参数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalQuery(BaseSchema):
    """云台查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    gimbal_name: Optional[str] = Field(None, description="云台名称（模糊查询）")
    map_id: Optional[str] = Field(None, description="地图ID筛选")


class GimbalListResponse(BaseSchema):
    """云台列表响应模式"""
    items: List[GimbalResponse] = Field(..., description="云台列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")

