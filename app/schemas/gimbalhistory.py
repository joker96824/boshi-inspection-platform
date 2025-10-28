"""
云台记录Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GimbalHistoryBase(BaseSchema):
    """云台记录基础模式"""
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")


class GimbalHistoryCreate(GimbalHistoryBase):
    """云台记录创建模式"""
    pass


class GimbalHistoryUpdate(BaseSchema):
    """云台记录更新模式"""
    gimbaltask_id: Optional[str] = Field(None, description="关联云台任务ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")


class GimbalHistoryResponse(BaseResponse):
    """云台记录响应模式"""
    id: str = Field(..., description="云台记录ID")
    gimbaltask_id: str = Field(..., description="关联云台任务ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, description="图像/视频链接")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalHistoryQuery(BaseSchema):
    """云台记录查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    gimbaltask_id: Optional[str] = Field(None, description="云台任务ID筛选")


class GimbalHistoryListResponse(BaseSchema):
    """云台记录列表响应模式"""
    items: List[GimbalHistoryResponse] = Field(..., description="云台记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
