"""
巡检中间表Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class PointItemBase(BaseSchema):
    """巡检中间表基础模式"""
    point_id: str = Field(..., description="巡检点ID")
    item_id: str = Field(..., description="巡检项目ID")


class PointItemCreate(PointItemBase):
    """巡检中间表创建模式"""
    pass


class PointItemUpdate(BaseSchema):
    """巡检中间表更新模式"""
    point_id: Optional[str] = Field(None, description="巡检点ID")
    item_id: Optional[str] = Field(None, description="巡检项目ID")


class PointItemResponse(BaseResponse):
    """巡检中间表响应模式"""
    id: str = Field(..., description="巡检中间表ID")
    point_id: str = Field(..., description="巡检点ID")
    item_id: str = Field(..., description="巡检项目ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class PointItemQuery(BaseSchema):
    """巡检中间表查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    point_ids: Optional[List[str]] = Field(None, description="巡检点ID列表（精确查询）")
    item_ids: Optional[List[str]] = Field(None, description="巡检项目ID列表（精确查询）")


class PointItemListResponse(BaseSchema):
    """巡检中间表列表响应模式"""
    items: List[PointItemResponse] = Field(..., description="巡检中间表列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")


class PointItemWithDetails(PointItemResponse):
    """带详情的巡检中间表响应模式"""
    point_name: Optional[str] = Field(None, description="巡检点名称")
    item_name: Optional[str] = Field(None, description="巡检项目名称")
    item_info: Optional[Dict[str, Any]] = Field(None, description="巡检项目信息")


class PointItemBatchUpdateByItem(BaseSchema):
    """通过巡检项目批量更新关联关系请求模式"""
    point_ids: List[str] = Field(..., description="巡检点ID列表")


class PointItemBatchUpdateByPoint(BaseSchema):
    """通过巡检点批量更新关联关系请求模式"""
    item_ids: List[str] = Field(..., description="巡检项目ID列表")
