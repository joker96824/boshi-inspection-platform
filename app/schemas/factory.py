"""
厂区数据验证模型
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class FactoryBase(BaseSchema):
    """厂区基础模式"""
    factory_name: str = Field(..., min_length=1, max_length=100, description="厂区名称")
    
    @validator('factory_name')
    def validate_factory_name(cls, v):
        if not v or not v.strip():
            raise ValueError("厂区名称不能为空")
        return v.strip()


class FactoryCreate(FactoryBase):
    """厂区创建模式"""
    pass


class FactoryUpdate(BaseSchema):
    """厂区更新模式"""
    factory_name: Optional[str] = Field(None, min_length=1, max_length=100, description="厂区名称")
    
    @validator('factory_name')
    def validate_factory_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError("厂区名称不能为空")
        return v.strip() if v else None


class FactoryResponse(BaseResponse):
    """厂区响应模式"""
    id: str = Field(..., description="厂区ID")
    factory_name: str = Field(..., description="厂区名称")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class FactoryQuery(BaseSchema):
    """厂区查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    factory_name: Optional[str] = Field(None, description="厂区名称筛选")


class FactoryListResponse(BaseSchema):
    """厂区列表响应模式"""
    items: List[FactoryResponse] = Field(..., description="厂区列表")
    total: int = Field(..., description="总数")

