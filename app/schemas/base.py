"""
基础Pydantic模式
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
# 使用字符串代替UUID


class BaseSchema(BaseModel):
    """基础模式类"""
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TimestampMixin(BaseSchema):
    """时间戳混入"""
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class IDMixin(BaseSchema):
    """ID混入"""
    id: str = Field(..., description="唯一标识")


class BaseResponse(IDMixin, TimestampMixin, BaseSchema):
    """基础响应模式"""
    created_by: Optional[str] = Field(None, description="创建人")
    updated_by: Optional[str] = Field(None, description="更新人")
    is_deleted: bool = Field(False, description="是否删除")


class PaginationParams(BaseSchema):
    """分页参数"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="排序方向")


class PaginationResponse(BaseSchema):
    """分页响应"""
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页数量")
    pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
