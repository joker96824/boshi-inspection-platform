"""
超声波状态配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from .base import BaseSchema, BaseResponse


class UltrasonicBase(BaseSchema):
    """超声波状态配置基础模式"""
    ultrasonic_id: int = Field(..., ge=0, le=255, description="超声波ID(0-255)")
    obstacle_avoidance_distance: Decimal = Field(800.00, ge=0.00, le=10000.00, description="超声波避障距离(mm)")
    deceleration_distance: Decimal = Field(1500.00, ge=0.00, le=10000.00, description="超声波减速距离(mm)")
    baud_rate: int = Field(9600, description="超声波波特率(9600-115200)")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if v not in valid_rates:
            raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v
    
    @validator('deceleration_distance')
    def validate_deceleration_distance(cls, v, values):
        if 'obstacle_avoidance_distance' in values and v <= values['obstacle_avoidance_distance']:
            raise ValueError('减速距离必须大于避障距离')
        return v


class UltrasonicCreate(UltrasonicBase):
    """超声波状态配置创建模式"""
    pass


class UltrasonicUpdate(BaseSchema):
    """超声波状态配置更新模式"""
    ultrasonic_id: Optional[int] = Field(None, ge=0, le=255, description="超声波ID(0-255)")
    obstacle_avoidance_distance: Optional[Decimal] = Field(None, ge=0.00, le=10000.00, description="超声波避障距离(mm)")
    deceleration_distance: Optional[Decimal] = Field(None, ge=0.00, le=10000.00, description="超声波减速距离(mm)")
    baud_rate: Optional[int] = Field(None, description="超声波波特率(9600-115200)")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        if v is not None:
            valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
            if v not in valid_rates:
                raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v


class UltrasonicResponse(BaseResponse):
    """超声波状态配置响应模式"""
    id: str = Field(..., description="超声波状态配置ID")
    ultrasonic_id: int = Field(..., description="超声波ID(0-255)")
    obstacle_avoidance_distance: Decimal = Field(..., description="超声波避障距离(mm)")
    deceleration_distance: Decimal = Field(..., description="超声波减速距离(mm)")
    baud_rate: int = Field(..., description="超声波波特率(9600-115200)")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class UltrasonicQuery(BaseSchema):
    """超声波状态配置查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    ultrasonic_id: Optional[int] = Field(None, description="超声波ID筛选")
    baud_rate: Optional[int] = Field(None, description="波特率筛选")
    obstacle_avoidance_distance_min: Optional[Decimal] = Field(None, description="避障距离最小值筛选")
    obstacle_avoidance_distance_max: Optional[Decimal] = Field(None, description="避障距离最大值筛选")


class UltrasonicListResponse(BaseSchema):
    """超声波状态配置列表响应模式"""
    items: List[UltrasonicResponse] = Field(..., description="超声波状态配置列表")
    total: int = Field(..., description="总数")
