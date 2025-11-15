"""
云台巡检记录Pydantic模式
"""

from typing import Any, Dict, List, Optional

from pydantic import Field

from .base import BaseResponse, BaseSchema


class GimbalHistoryBase(BaseSchema):
    """云台巡检记录基础模式"""

    inspection_project_id: str = Field(..., description="关联云台巡检项目ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")


class GimbalHistoryCreate(GimbalHistoryBase):
    """云台巡检记录创建模式"""


class GimbalHistoryUpdate(BaseSchema):
    """云台巡检记录更新模式"""

    inspection_project_id: Optional[str] = Field(
        None, description="关联云台巡检项目ID"
    )
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, max_length=500, description="图像/视频链接")


class GimbalHistoryResponse(BaseResponse):
    """云台巡检记录响应模式"""

    id: str = Field(..., description="云台记录ID")
    inspection_project_id: str = Field(..., description="关联云台巡检项目ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    media_url: Optional[str] = Field(None, description="图像/视频链接")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalHistoryQuery(BaseSchema):
    """云台巡检记录查询模式"""

    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    inspection_project_id: Optional[str] = Field(
        None, description="云台巡检项目ID筛选"
    )


class GimbalHistoryListResponse(BaseSchema):
    """云台巡检记录列表响应模式"""

    items: List[GimbalHistoryResponse] = Field(..., description="云台巡检记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
