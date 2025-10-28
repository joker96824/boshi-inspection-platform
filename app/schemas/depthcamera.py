"""
深度相机配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from .base import BaseSchema, BaseResponse


class DepthCameraBase(BaseSchema):
    """深度相机配置基础模式"""
    camera_type: str = Field("RGB-D", description="深度相机类型")
    resolution_width: int = Field(640, ge=320, le=4096, description="分辨率宽度")
    resolution_height: int = Field(480, ge=240, le=4096, description="分辨率高度")
    frame_rate: int = Field(30, ge=1, le=120, description="帧率(fps)")
    depth_range_min: Decimal = Field(0.10, ge=0.01, le=100.00, description="最小深度范围(m)")
    depth_range_max: Decimal = Field(10.00, ge=0.01, le=100.00, description="最大深度范围(m)")
    depth_accuracy: Decimal = Field(0.0010, ge=0.0001, le=1.0000, description="深度精度(m)")
    camera_ip: Optional[str] = Field(None, description="相机IP地址")
    camera_port: Optional[int] = Field(None, ge=1, le=65535, description="相机端口号")
    protocol: str = Field("USB", description="连接协议")
    exposure_time: Optional[int] = Field(None, ge=1, le=100000, description="曝光时间(μs)")
    gain: Optional[Decimal] = Field(None, ge=0.00, le=10.00, description="增益值")
    white_balance: str = Field("Auto", description="白平衡模式")
    
    @validator('camera_type')
    def validate_camera_type(cls, v):
        valid_types = ['RGB-D', 'ToF', 'Stereo', 'Structured_Light']
        if v not in valid_types:
            raise ValueError(f'相机类型必须是以下值之一: {valid_types}')
        return v
    
    @validator('protocol')
    def validate_protocol(cls, v):
        valid_protocols = ['USB', 'Ethernet', 'WiFi', 'Serial']
        if v not in valid_protocols:
            raise ValueError(f'连接协议必须是以下值之一: {valid_protocols}')
        return v
    
    @validator('white_balance')
    def validate_white_balance(cls, v):
        valid_balances = ['Auto', 'Manual', 'Daylight', 'Fluorescent', 'Tungsten']
        if v not in valid_balances:
            raise ValueError(f'白平衡模式必须是以下值之一: {valid_balances}')
        return v
    
    @validator('camera_ip')
    def validate_camera_ip(cls, v):
        if v is not None:
            import re
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, v):
                raise ValueError('IP地址格式不正确')
            
            parts = v.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError('IP地址范围不正确')
        return v
    
    @validator('depth_range_max')
    def validate_depth_range_max(cls, v, values):
        if 'depth_range_min' in values and v <= values['depth_range_min']:
            raise ValueError('最大深度范围必须大于最小深度范围')
        return v


class DepthCameraCreate(DepthCameraBase):
    """深度相机配置创建模式"""
    pass


class DepthCameraUpdate(BaseSchema):
    """深度相机配置更新模式"""
    camera_type: Optional[str] = Field(None, description="深度相机类型")
    resolution_width: Optional[int] = Field(None, ge=320, le=4096, description="分辨率宽度")
    resolution_height: Optional[int] = Field(None, ge=240, le=4096, description="分辨率高度")
    frame_rate: Optional[int] = Field(None, ge=1, le=120, description="帧率(fps)")
    depth_range_min: Optional[Decimal] = Field(None, ge=0.01, le=100.00, description="最小深度范围(m)")
    depth_range_max: Optional[Decimal] = Field(None, ge=0.01, le=100.00, description="最大深度范围(m)")
    depth_accuracy: Optional[Decimal] = Field(None, ge=0.0001, le=1.0000, description="深度精度(m)")
    camera_ip: Optional[str] = Field(None, description="相机IP地址")
    camera_port: Optional[int] = Field(None, ge=1, le=65535, description="相机端口号")
    protocol: Optional[str] = Field(None, description="连接协议")
    exposure_time: Optional[int] = Field(None, ge=1, le=100000, description="曝光时间(μs)")
    gain: Optional[Decimal] = Field(None, ge=0.00, le=10.00, description="增益值")
    white_balance: Optional[str] = Field(None, description="白平衡模式")
    
    @validator('camera_type')
    def validate_camera_type(cls, v):
        if v is not None:
            valid_types = ['RGB-D', 'ToF', 'Stereo', 'Structured_Light']
            if v not in valid_types:
                raise ValueError(f'相机类型必须是以下值之一: {valid_types}')
        return v
    
    @validator('protocol')
    def validate_protocol(cls, v):
        if v is not None:
            valid_protocols = ['USB', 'Ethernet', 'WiFi', 'Serial']
            if v not in valid_protocols:
                raise ValueError(f'连接协议必须是以下值之一: {valid_protocols}')
        return v
    
    @validator('white_balance')
    def validate_white_balance(cls, v):
        if v is not None:
            valid_balances = ['Auto', 'Manual', 'Daylight', 'Fluorescent', 'Tungsten']
            if v not in valid_balances:
                raise ValueError(f'白平衡模式必须是以下值之一: {valid_balances}')
        return v
    
    @validator('camera_ip')
    def validate_camera_ip(cls, v):
        if v is not None:
            import re
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, v):
                raise ValueError('IP地址格式不正确')
            
            parts = v.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError('IP地址范围不正确')
        return v


class DepthCameraResponse(BaseResponse):
    """深度相机配置响应模式"""
    id: str = Field(..., description="深度相机配置ID")
    camera_type: str = Field(..., description="深度相机类型")
    resolution_width: int = Field(..., description="分辨率宽度")
    resolution_height: int = Field(..., description="分辨率高度")
    frame_rate: int = Field(..., description="帧率(fps)")
    depth_range_min: Decimal = Field(..., description="最小深度范围(m)")
    depth_range_max: Decimal = Field(..., description="最大深度范围(m)")
    depth_accuracy: Decimal = Field(..., description="深度精度(m)")
    camera_ip: Optional[str] = Field(None, description="相机IP地址")
    camera_port: Optional[int] = Field(None, description="相机端口号")
    protocol: str = Field(..., description="连接协议")
    exposure_time: Optional[int] = Field(None, description="曝光时间(μs)")
    gain: Optional[Decimal] = Field(None, description="增益值")
    white_balance: str = Field(..., description="白平衡模式")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class DepthCameraQuery(BaseSchema):
    """深度相机配置查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    camera_type: Optional[str] = Field(None, description="相机类型筛选")
    protocol: Optional[str] = Field(None, description="连接协议筛选")
    frame_rate: Optional[int] = Field(None, description="帧率筛选")
    camera_ip: Optional[str] = Field(None, description="相机IP筛选")


class DepthCameraListResponse(BaseSchema):
    """深度相机配置列表响应模式"""
    items: List[DepthCameraResponse] = Field(..., description="深度相机配置列表")
    total: int = Field(..., description="总数")

