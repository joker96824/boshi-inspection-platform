"""
导航控制器配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from .base import BaseSchema, BaseResponse


class NavigationControllerBase(BaseSchema):
    """导航控制器配置基础模式"""
    module_group: int = Field(1, ge=1, le=10, description="模块组编号(支持多组配置)")
    ethernet_ip: str = Field(..., description="以太网通讯IP地址")
    subnet_mask: str = Field("255.255.255.0", description="子网掩码")
    gateway: str = Field("192.168.1.1", description="网关地址")
    ethernet_port: int = Field(..., ge=1, le=65535, description="以太网通讯端口号(1-65535)")
    baud_rate: int = Field(9600, description="波特率(9600-115200)")
    deceleration_distance: Decimal = Field(800.00, ge=0.00, le=10000.00, description="减速距离(mm)")
    stop_distance: Decimal = Field(1500.00, ge=0.00, le=10000.00, description="停止距离(mm)")
    max_linear_velocity: Decimal = Field(0.800, ge=0.001, le=10.000, description="路径最大线速度(m/s)")
    max_angular_velocity: Decimal = Field(0.100, ge=0.001, le=10.000, description="路径最大角速度(rad/s)")
    acceleration: Decimal = Field(0.800, ge=0.001, le=10.000, description="加速度(m/s²)")
    deceleration: Decimal = Field(0.800, ge=0.001, le=10.000, description="减速度(m/s²)")
    expansion_coefficient: Decimal = Field(0.00, ge=0.00, le=2.00, description="膨胀系数(0-2.0)")
    
    @validator('ethernet_ip')
    def validate_ethernet_ip(cls, v):
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('IP地址格式不正确')
        
        parts = v.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError('IP地址范围不正确')
        return v
    
    @validator('subnet_mask')
    def validate_subnet_mask(cls, v):
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('子网掩码格式不正确')
        
        parts = v.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError('子网掩码范围不正确')
        return v
    
    @validator('gateway')
    def validate_gateway(cls, v):
        import re
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, v):
            raise ValueError('网关地址格式不正确')
        
        parts = v.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                raise ValueError('网关地址范围不正确')
        return v
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if v not in valid_rates:
            raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v
    
    @validator('stop_distance')
    def validate_stop_distance(cls, v, values):
        if 'deceleration_distance' in values and v <= values['deceleration_distance']:
            raise ValueError('停止距离必须大于减速距离')
        return v


class NavigationControllerCreate(NavigationControllerBase):
    """导航控制器配置创建模式"""
    pass


class NavigationControllerUpdate(BaseSchema):
    """导航控制器配置更新模式"""
    module_group: Optional[int] = Field(None, ge=1, le=10, description="模块组编号(支持多组配置)")
    ethernet_ip: Optional[str] = Field(None, description="以太网通讯IP地址")
    subnet_mask: Optional[str] = Field(None, description="子网掩码")
    gateway: Optional[str] = Field(None, description="网关地址")
    ethernet_port: Optional[int] = Field(None, ge=1, le=65535, description="以太网通讯端口号(1-65535)")
    baud_rate: Optional[int] = Field(None, description="波特率(9600-115200)")
    deceleration_distance: Optional[Decimal] = Field(None, ge=0.00, le=10000.00, description="减速距离(mm)")
    stop_distance: Optional[Decimal] = Field(None, ge=0.00, le=10000.00, description="停止距离(mm)")
    max_linear_velocity: Optional[Decimal] = Field(None, ge=0.001, le=10.000, description="路径最大线速度(m/s)")
    max_angular_velocity: Optional[Decimal] = Field(None, ge=0.001, le=10.000, description="路径最大角速度(rad/s)")
    acceleration: Optional[Decimal] = Field(None, ge=0.001, le=10.000, description="加速度(m/s²)")
    deceleration: Optional[Decimal] = Field(None, ge=0.001, le=10.000, description="减速度(m/s²)")
    expansion_coefficient: Optional[Decimal] = Field(None, ge=0.00, le=2.00, description="膨胀系数(0-2.0)")
    
    @validator('ethernet_ip')
    def validate_ethernet_ip(cls, v):
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
    
    @validator('subnet_mask')
    def validate_subnet_mask(cls, v):
        if v is not None:
            import re
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, v):
                raise ValueError('子网掩码格式不正确')
            
            parts = v.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError('子网掩码范围不正确')
        return v
    
    @validator('gateway')
    def validate_gateway(cls, v):
        if v is not None:
            import re
            ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
            if not re.match(ip_pattern, v):
                raise ValueError('网关地址格式不正确')
            
            parts = v.split('.')
            for part in parts:
                if not 0 <= int(part) <= 255:
                    raise ValueError('网关地址范围不正确')
        return v
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        if v is not None:
            valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
            if v not in valid_rates:
                raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v


class NavigationControllerResponse(BaseResponse):
    """导航控制器配置响应模式"""
    id: str = Field(..., description="导航控制器配置ID")
    module_group: int = Field(..., description="模块组编号(支持多组配置)")
    ethernet_ip: str = Field(..., description="以太网通讯IP地址")
    subnet_mask: str = Field(..., description="子网掩码")
    gateway: str = Field(..., description="网关地址")
    ethernet_port: int = Field(..., description="以太网通讯端口号(1-65535)")
    baud_rate: int = Field(..., description="波特率(9600-115200)")
    deceleration_distance: Decimal = Field(..., description="减速距离(mm)")
    stop_distance: Decimal = Field(..., description="停止距离(mm)")
    max_linear_velocity: Decimal = Field(..., description="路径最大线速度(m/s)")
    max_angular_velocity: Decimal = Field(..., description="路径最大角速度(rad/s)")
    acceleration: Decimal = Field(..., description="加速度(m/s²)")
    deceleration: Decimal = Field(..., description="减速度(m/s²)")
    expansion_coefficient: Decimal = Field(..., description="膨胀系数(0-2.0)")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class NavigationControllerQuery(BaseSchema):
    """导航控制器配置查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    module_group: Optional[int] = Field(None, description="模块组筛选")
    ethernet_ip: Optional[str] = Field(None, description="以太网IP筛选")
    ethernet_port: Optional[int] = Field(None, description="以太网端口筛选")
    baud_rate: Optional[int] = Field(None, description="波特率筛选")


class NavigationControllerListResponse(BaseSchema):
    """导航控制器配置列表响应模式"""
    items: List[NavigationControllerResponse] = Field(..., description="导航控制器配置列表")
    total: int = Field(..., description="总数")
