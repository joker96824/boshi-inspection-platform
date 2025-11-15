"""
传感器记录Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class SensorHistoryBase(BaseSchema):
    """传感器记录基础模式"""
    sensor_id: str = Field(..., description="关联传感器ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    file_url: Optional[str] = Field(None, max_length=500, description="相关文件链接")


class SensorHistoryCreate(SensorHistoryBase):
    """传感器记录创建模式"""
    pass


class SensorHistoryUpdate(BaseSchema):
    """传感器记录更新模式"""
    sensor_id: Optional[str] = Field(None, description="关联传感器ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    file_url: Optional[str] = Field(None, max_length=500, description="相关文件链接")


class SensorHistoryResponse(BaseResponse):
    """传感器记录响应模式"""
    id: str = Field(..., description="传感器记录ID")
    sensor_id: str = Field(..., description="关联传感器ID")
    record_data: Optional[Dict[str, Any]] = Field(None, description="记录数据")
    file_url: Optional[str] = Field(None, description="相关文件链接")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class SensorHistoryQuery(BaseSchema):
    """传感器记录查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    sensor_id: Optional[str] = Field(None, description="传感器ID筛选")


class SensorHistoryListResponse(BaseSchema):
    """传感器记录列表响应模式"""
    items: List[SensorHistoryResponse] = Field(..., description="传感器记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
