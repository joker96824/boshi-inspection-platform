"""
深度相机配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class DepthCameraBase(BaseSchema):
    """深度相机配置基础模式"""
    serial_port_id: int = Field(0, ge=0, le=255, description="串口ID(0-255)")
    camera_mode: Optional[str] = Field(None, description="相机模式")
    image_flip: Optional[str] = Field(None, description="图像翻转")
    image_alignment: Optional[str] = Field(None, description="图像对齐")
    
    @validator('image_flip')
    def validate_image_flip(cls, v):
        if v is not None:
            valid_flips = ['上下翻转', '左右翻转', '中心翻转']
            if v not in valid_flips:
                raise ValueError(f'图像翻转必须是以下值之一: {valid_flips}')
        return v


class DepthCameraCreate(DepthCameraBase):
    """深度相机配置创建模式"""
    pass


class DepthCameraUpdate(BaseSchema):
    """深度相机配置更新模式"""
    serial_port_id: Optional[int] = Field(None, ge=0, le=255, description="串口ID(0-255)")
    camera_mode: Optional[str] = Field(None, description="相机模式")
    image_flip: Optional[str] = Field(None, description="图像翻转")
    image_alignment: Optional[str] = Field(None, description="图像对齐")
    
    @validator('image_flip')
    def validate_image_flip(cls, v):
        if v is not None:
            valid_flips = ['上下翻转', '左右翻转', '中心翻转']
            if v not in valid_flips:
                raise ValueError(f'图像翻转必须是以下值之一: {valid_flips}')
        return v


class DepthCameraResponse(BaseResponse):
    """深度相机配置响应模式"""
    id: str = Field(..., description="深度相机配置ID")
    robot_id: str = Field(..., description="关联机器人ID")
    serial_port_id: int = Field(..., description="串口ID(0-255)")
    camera_mode: Optional[str] = Field(None, description="相机模式")
    image_flip: Optional[str] = Field(None, description="图像翻转")
    image_alignment: Optional[str] = Field(None, description="图像对齐")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class DepthCameraQuery(BaseSchema):
    """深度相机配置查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    serial_port_id: Optional[int] = Field(None, description="串口ID筛选")
    camera_mode: Optional[str] = Field(None, description="相机模式筛选")


class DepthCameraListResponse(BaseSchema):
    """深度相机配置列表响应模式"""
    items: List[DepthCameraResponse] = Field(..., description="深度相机配置列表")
    total: int = Field(..., description="总数")


class DepthCameraBatchUpdate(BaseSchema):
    """深度相机配置批量更新模式（按机器人）"""
    robot_id: str = Field(..., description="机器人ID")
    configs: List[DepthCameraCreate] = Field(..., description="深度相机配置列表")
