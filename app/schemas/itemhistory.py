"""
巡检记录Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class ItemHistoryBase(BaseSchema):
    """巡检记录基础模式"""
    taskhistory_id: str = Field(..., description="任务记录ID")
    item_id: str = Field(..., description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")


class ItemHistoryCreate(ItemHistoryBase):
    """巡检记录创建模式"""
    pass


class ItemHistoryUpdate(BaseSchema):
    """巡检记录更新模式"""
    taskhistory_id: Optional[str] = Field(None, description="任务记录ID")
    item_id: Optional[str] = Field(None, description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")


class ItemHistoryResponse(BaseResponse):
    """巡检记录响应模式"""
    id: str = Field(..., description="巡检记录ID")
    taskhistory_id: str = Field(..., description="任务记录ID")
    item_id: str = Field(..., description="巡检项目ID")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class ItemHistoryQuery(BaseSchema):
    """巡检记录查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    taskhistory_id: Optional[str] = Field(None, description="任务记录ID（精确查询）")
    item_id: Optional[str] = Field(None, description="巡检项目ID（精确查询）")
    taskhistory_ids: Optional[List[str]] = Field(None, description="任务记录ID列表（精确查询）")
    item_ids: Optional[List[str]] = Field(None, description="巡检项目ID列表（精确查询）")


class ItemHistoryListResponse(BaseSchema):
    """巡检记录列表响应模式"""
    items: List[ItemHistoryResponse] = Field(..., description="巡检记录列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")


class ItemHistoryWithDetails(ItemHistoryResponse):
    """带详情的巡检记录响应模式"""
    task_name: Optional[str] = Field(None, description="任务名称")
    item_name: Optional[str] = Field(None, description="巡检项目名称")
    item_info: Optional[Dict[str, Any]] = Field(None, description="巡检项目信息")
    item_result: Optional[Dict[str, Any]] = Field(None, description="巡检结果")
