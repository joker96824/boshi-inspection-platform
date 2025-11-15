"""
环境传感器数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class EnvironmentSensorBase(BaseSchema):
    """环境传感器基础模式"""
    station_number: int = Field(..., ge=1, le=255, description="站号(1-255)")
    baud_rate: int = Field(..., description="波特率(9600-115200)")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if v not in valid_rates:
            raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v


class EnvironmentSensorCreate(EnvironmentSensorBase):
    """环境传感器创建模式"""
    pass


class EnvironmentSensorUpdate(BaseSchema):
    """环境传感器更新模式"""
    station_number: Optional[int] = Field(None, ge=1, le=255, description="站号(1-255)")
    baud_rate: Optional[int] = Field(None, description="波特率(9600-115200)")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        if v is not None:
            valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
            if v not in valid_rates:
                raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v


class EnvironmentSensorResponse(BaseResponse):
    """环境传感器响应模式"""
    id: str = Field(..., description="环境传感器ID")
    station_number: int = Field(..., description="站号(1-255)")
    baud_rate: int = Field(..., description="波特率(9600-115200)")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class EnvironmentSensorQuery(BaseSchema):
    """环境传感器查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    station_number: Optional[int] = Field(None, description="站号筛选")
    baud_rate: Optional[int] = Field(None, description="波特率筛选")


class EnvironmentSensorListResponse(BaseSchema):
    """环境传感器列表响应模式"""
    items: List[EnvironmentSensorResponse] = Field(..., description="环境传感器列表")
    total: int = Field(..., description="总数")

