"""
双光云台配置数据验证模式
"""

from typing import Optional, List
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class DualPTZBase(BaseSchema):
    """双光云台配置基础模式"""
    ptz_ip: str = Field(..., description="云台IP地址")
    subnet_mask: str = Field("255.255.255.0", description="子网掩码")
    gateway: str = Field("192.168.1.1", description="网关地址")
    operating_speed: int = Field(100, ge=1, le=255, description="运行速度(1-255)")
    fill_light_enabled: bool = Field(False, description="补光灯开启状态")
    wiper_enabled: bool = Field(False, description="雨刷开启状态")
    auto_focus_enabled: bool = Field(True, description="自动对焦开启状态")
    backlight_compensation_enabled: bool = Field(False, description="逆光补偿开启状态")
    
    @validator('ptz_ip')
    def validate_ptz_ip(cls, v):
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


class DualPTZCreate(DualPTZBase):
    """双光云台配置创建模式"""
    pass


class DualPTZUpdate(BaseSchema):
    """双光云台配置更新模式"""
    ptz_ip: Optional[str] = Field(None, description="云台IP地址")
    subnet_mask: Optional[str] = Field(None, description="子网掩码")
    gateway: Optional[str] = Field(None, description="网关地址")
    operating_speed: Optional[int] = Field(None, ge=1, le=255, description="运行速度(1-255)")
    fill_light_enabled: Optional[bool] = Field(None, description="补光灯开启状态")
    wiper_enabled: Optional[bool] = Field(None, description="雨刷开启状态")
    auto_focus_enabled: Optional[bool] = Field(None, description="自动对焦开启状态")
    backlight_compensation_enabled: Optional[bool] = Field(None, description="逆光补偿开启状态")
    
    @validator('ptz_ip')
    def validate_ptz_ip(cls, v):
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


class DualPTZResponse(BaseResponse):
    """双光云台配置响应模式"""
    id: str = Field(..., description="双光云台配置ID")
    robot_id: str = Field(..., description="关联机器人ID")
    ptz_ip: str = Field(..., description="云台IP地址")
    subnet_mask: str = Field(..., description="子网掩码")
    gateway: str = Field(..., description="网关地址")
    operating_speed: int = Field(..., description="运行速度(1-255)")
    fill_light_enabled: bool = Field(..., description="补光灯开启状态")
    wiper_enabled: bool = Field(..., description="雨刷开启状态")
    auto_focus_enabled: bool = Field(..., description="自动对焦开启状态")
    backlight_compensation_enabled: bool = Field(..., description="逆光补偿开启状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class DualPTZQuery(BaseSchema):
    """双光云台配置查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    ptz_ip: Optional[str] = Field(None, description="云台IP筛选")
    operating_speed: Optional[int] = Field(None, description="运行速度筛选")


class DualPTZListResponse(BaseSchema):
    """双光云台配置列表响应模式"""
    items: List[DualPTZResponse] = Field(..., description="双光云台配置列表")
    total: int = Field(..., description="总数")


class DualPTZBatchUpdate(BaseSchema):
    """双光云台配置批量更新模式（按机器人）"""
    robot_id: str = Field(..., description="机器人ID")
    configs: List[DualPTZCreate] = Field(..., description="双光云台配置列表")
