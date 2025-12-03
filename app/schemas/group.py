"""
分组数据验证模式
"""

from typing import Optional
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GroupBase(BaseSchema):
    """分组基础模式"""
    group_name: str = Field(..., min_length=1, max_length=100, description="分组名称")
    group_description: Optional[str] = Field(None, max_length=500, description="分组描述")


class GroupCreate(GroupBase):
    """分组创建模式"""
    pass


class GroupUpdate(BaseSchema):
    """分组更新模式"""
    group_name: Optional[str] = Field(None, min_length=1, max_length=100, description="分组名称")
    group_description: Optional[str] = Field(None, max_length=500, description="分组描述")


class GroupResponse(BaseResponse):
    """分组响应模式"""
    id: str = Field(..., description="分组ID")
    group_name: str = Field(..., description="分组名称")
    group_description: Optional[str] = Field(None, description="分组描述")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GroupQuery(BaseSchema):
    """分组查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    group_name: Optional[str] = Field(None, description="分组名称（模糊查询）")

