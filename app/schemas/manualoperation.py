"""
手动操作记录数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base import BaseSchema, BaseResponse


class ManualOperationBase(BaseSchema):
    """手动操作记录基础模式"""
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., max_length=50, description="用户名")
    operation_time: datetime = Field(..., description="操作时间")
    operation_content: Dict[str, Any] = Field(..., description="操作内容JSON")


class ManualOperationCreate(ManualOperationBase):
    """手动操作记录创建模式"""
    pass


class ManualOperationUpdate(BaseSchema):
    """手动操作记录更新模式"""
    user_id: Optional[str] = Field(None, description="用户ID")
    username: Optional[str] = Field(None, max_length=50, description="用户名")
    operation_time: Optional[datetime] = Field(None, description="操作时间")
    operation_content: Optional[Dict[str, Any]] = Field(None, description="操作内容JSON")


class ManualOperationResponse(BaseResponse):
    """手动操作记录响应模式"""
    id: str = Field(..., description="手动操作记录ID")
    user_id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    operation_time: str = Field(..., description="操作时间")
    operation_content: Dict[str, Any] = Field(..., description="操作内容JSON")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class ManualOperationQuery(BaseSchema):
    """手动操作记录查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    user_id: Optional[str] = Field(None, description="用户ID筛选")
    username: Optional[str] = Field(None, description="用户名筛选")
    start_time: Optional[datetime] = Field(None, description="开始时间筛选")
    end_time: Optional[datetime] = Field(None, description="结束时间筛选")


class ManualOperationListResponse(BaseSchema):
    """手动操作记录列表响应模式"""
    items: List[ManualOperationResponse] = Field(..., description="手动操作记录列表")
    total: int = Field(..., description="总数")
