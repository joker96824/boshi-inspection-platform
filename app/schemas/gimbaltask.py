"""
云台任务Pydantic模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import BaseSchema, BaseResponse


class GimbalTaskBase(BaseSchema):
    """云台任务基础模式"""
    task_name: str = Field(..., min_length=1, max_length=100, description="云台任务名称")
    angle_params: Optional[Dict[str, Any]] = Field(None, description="角度参数")
    task_type: str = Field(..., description="任务类别：image/video")
    gimbal_id: str = Field(..., description="所属云台ID")


class GimbalTaskCreate(GimbalTaskBase):
    """云台任务创建模式"""
    pass


class GimbalTaskUpdate(BaseSchema):
    """云台任务更新模式"""
    task_name: Optional[str] = Field(None, min_length=1, max_length=100, description="云台任务名称")
    angle_params: Optional[Dict[str, Any]] = Field(None, description="角度参数")
    task_type: Optional[str] = Field(None, description="任务类别：image/video")
    gimbal_id: Optional[str] = Field(None, description="所属云台ID")


class GimbalTaskResponse(BaseResponse):
    """云台任务响应模式"""
    id: str = Field(..., description="云台任务ID")
    task_name: str = Field(..., description="云台任务名称")
    angle_params: Optional[Dict[str, Any]] = Field(None, description="角度参数")
    task_type: str = Field(..., description="任务类别：image/video")
    gimbal_id: str = Field(..., description="所属云台ID")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class GimbalTaskQuery(BaseSchema):
    """云台任务查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    task_name: Optional[str] = Field(None, description="云台任务名称（模糊查询）")
    task_type: Optional[str] = Field(None, description="任务类别筛选")
    gimbal_id: Optional[str] = Field(None, description="云台ID筛选")


class GimbalTaskListResponse(BaseSchema):
    """云台任务列表响应模式"""
    items: List[GimbalTaskResponse] = Field(..., description="云台任务列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
