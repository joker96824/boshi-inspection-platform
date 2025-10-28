"""
巡检项目Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class ItemBase(BaseSchema):
    """巡检项目基础模式"""
    item_name: str = Field(..., min_length=1, max_length=100, description="巡检项目名称")
    item_info: Dict[str, Any] = Field(..., description="巡检参数信息")
    point_id: str = Field(..., description="所属巡检点ID")


class ItemCreate(ItemBase):
    """巡检项目创建模式"""
    pass


class ItemUpdate(BaseSchema):
    """巡检项目更新模式"""
    item_name: Optional[str] = Field(None, min_length=1, max_length=100, description="巡检项目名称")
    item_info: Optional[Dict[str, Any]] = Field(None, description="巡检参数信息")
    point_id: Optional[str] = Field(None, description="所属巡检点ID")


class ItemResponse(BaseResponse):
    """巡检项目响应模式"""
    id: str = Field(..., description="巡检项目ID")
    item_name: str = Field(..., description="巡检项目名称")
    item_info: Dict[str, Any] = Field(..., description="巡检参数信息")
    point_id: str = Field(..., description="所属巡检点ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class ItemQuery(BaseSchema):
    """巡检项目查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    item_name: Optional[str] = Field(None, description="巡检项目名称（模糊查询）")
    point_id: Optional[str] = Field(None, description="巡检点ID（筛选）")


class ItemListResponse(BaseSchema):
    """巡检项目列表响应模式"""
    items: List[ItemResponse] = Field(..., description="巡检项目列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
