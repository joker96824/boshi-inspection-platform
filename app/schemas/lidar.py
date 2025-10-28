"""
激光雷达配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from .base import BaseSchema, BaseResponse


class LidarBase(BaseSchema):
    """激光雷达配置基础模式"""
    lidar_ip: str = Field(..., description="激光雷达IP地址")
    subnet_mask: str = Field("255.255.255.0", description="子网掩码")
    gateway: str = Field("192.168.1.1", description="网关地址")
    lidar_port: int = Field(..., ge=1, le=65535, description="激光雷达端口(1-65535)")
    scan_frequency_rpm: int = Field(2000, ge=1, le=10000, description="雷达扫描频率/转速Rpm")
    x_coordinate: Decimal = Field(0.00, ge=-999999.99, le=999999.99, description="X坐标")
    y_coordinate: Decimal = Field(0.00, ge=-999999.99, le=999999.99, description="Y坐标")
    z_coordinate: Decimal = Field(0.00, ge=-999999.99, le=999999.99, description="Z坐标")
    scan_range_min: Decimal = Field(0.00, ge=0.00, le=360.00, description="扫描范围最小值(度)")
    scan_range_max: Decimal = Field(360.00, ge=0.00, le=360.00, description="扫描范围最大值(度)")
    scan_distance_min: Decimal = Field(0.00, ge=0.00, le=1000.00, description="扫描距离最小值(米)")
    scan_distance_max: Decimal = Field(100.00, ge=0.00, le=1000.00, description="扫描距离最大值(米)")
    
    @validator('lidar_ip')
    def validate_lidar_ip(cls, v):
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
    
    @validator('scan_range_max')
    def validate_scan_range(cls, v, values):
        if 'scan_range_min' in values and v <= values['scan_range_min']:
            raise ValueError('扫描范围最大值必须大于最小值')
        return v
    
    @validator('scan_distance_max')
    def validate_scan_distance(cls, v, values):
        if 'scan_distance_min' in values and v <= values['scan_distance_min']:
            raise ValueError('扫描距离最大值必须大于最小值')
        return v


class LidarCreate(LidarBase):
    """激光雷达配置创建模式"""
    pass


class LidarUpdate(BaseSchema):
    """激光雷达配置更新模式"""
    lidar_ip: Optional[str] = Field(None, description="激光雷达IP地址")
    subnet_mask: Optional[str] = Field(None, description="子网掩码")
    gateway: Optional[str] = Field(None, description="网关地址")
    lidar_port: Optional[int] = Field(None, ge=1, le=65535, description="激光雷达端口(1-65535)")
    scan_frequency_rpm: Optional[int] = Field(None, ge=1, le=10000, description="雷达扫描频率/转速Rpm")
    x_coordinate: Optional[Decimal] = Field(None, ge=-999999.99, le=999999.99, description="X坐标")
    y_coordinate: Optional[Decimal] = Field(None, ge=-999999.99, le=999999.99, description="Y坐标")
    z_coordinate: Optional[Decimal] = Field(None, ge=-999999.99, le=999999.99, description="Z坐标")
    scan_range_min: Optional[Decimal] = Field(None, ge=0.00, le=360.00, description="扫描范围最小值(度)")
    scan_range_max: Optional[Decimal] = Field(None, ge=0.00, le=360.00, description="扫描范围最大值(度)")
    scan_distance_min: Optional[Decimal] = Field(None, ge=0.00, le=1000.00, description="扫描距离最小值(米)")
    scan_distance_max: Optional[Decimal] = Field(None, ge=0.00, le=1000.00, description="扫描距离最大值(米)")
    
    @validator('lidar_ip')
    def validate_lidar_ip(cls, v):
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


class LidarResponse(BaseResponse):
    """激光雷达配置响应模式"""
    id: str = Field(..., description="激光雷达配置ID")
    lidar_ip: str = Field(..., description="激光雷达IP地址")
    subnet_mask: str = Field(..., description="子网掩码")
    gateway: str = Field(..., description="网关地址")
    lidar_port: int = Field(..., description="激光雷达端口(1-65535)")
    scan_frequency_rpm: int = Field(..., description="雷达扫描频率/转速Rpm")
    x_coordinate: Decimal = Field(..., description="X坐标")
    y_coordinate: Decimal = Field(..., description="Y坐标")
    z_coordinate: Decimal = Field(..., description="Z坐标")
    scan_range_min: Decimal = Field(..., description="扫描范围最小值(度)")
    scan_range_max: Decimal = Field(..., description="扫描范围最大值(度)")
    scan_distance_min: Decimal = Field(..., description="扫描距离最小值(米)")
    scan_distance_max: Decimal = Field(..., description="扫描距离最大值(米)")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class LidarQuery(BaseSchema):
    """激光雷达配置查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    lidar_ip: Optional[str] = Field(None, description="激光雷达IP筛选")
    lidar_port: Optional[int] = Field(None, description="激光雷达端口筛选")
    scan_frequency_rpm: Optional[int] = Field(None, description="扫描频率筛选")


class LidarListResponse(BaseSchema):
    """激光雷达配置列表响应模式"""
    items: List[LidarResponse] = Field(..., description="激光雷达配置列表")
    total: int = Field(..., description="总数")
