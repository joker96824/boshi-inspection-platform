"""
机械臂状态配置数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from decimal import Decimal
from .base import BaseSchema, BaseResponse


class RobotArmBase(BaseSchema):
    """机械臂状态配置基础模式"""
    robot_arm_ip: str = Field(..., description="机械臂IP地址")
    subnet_mask: str = Field("255.255.255.0", description="子网掩码")
    gateway: str = Field("192.168.1.1", description="网关地址")
    robot_arm_port: int = Field(..., ge=1, le=65535, description="机械臂端口号(1-65535)")
    operating_speed: int = Field(50, ge=0, le=100, description="机械臂运行速度(0-100%)")
    origin_coordinates: List[float] = Field(..., min_items=6, max_items=6, description="机械臂原点坐标(6个数值)")
    plane_coordinates: List[float] = Field(..., min_items=6, max_items=6, description="机械臂平面坐标(6个数值)")
    load_size: Decimal = Field(0.50, ge=0.00, le=100.00, description="机械臂负载大小(kg)")
    end_coordinates: List[float] = Field(..., min_items=6, max_items=6, description="机械臂末端坐标(6个数值)")
    tool_io: int = Field(0, ge=0, le=255, description="机械臂工具IO(0-255)")
    collision_detection_level: str = Field("中", description="机械臂碰撞检测级别")
    
    @validator('robot_arm_ip')
    def validate_robot_arm_ip(cls, v):
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
    
    @validator('collision_detection_level')
    def validate_collision_level(cls, v):
        if v not in ['低', '中', '高']:
            raise ValueError('碰撞检测级别必须是: 低、中、高')
        return v
    
    @validator('origin_coordinates')
    def validate_origin_coordinates(cls, v):
        if len(v) != 6:
            raise ValueError('原点坐标必须包含6个数值')
        return v
    
    @validator('plane_coordinates')
    def validate_plane_coordinates(cls, v):
        if len(v) != 6:
            raise ValueError('平面坐标必须包含6个数值')
        return v
    
    @validator('end_coordinates')
    def validate_end_coordinates(cls, v):
        if len(v) != 6:
            raise ValueError('末端坐标必须包含6个数值')
        return v


class RobotArmCreate(RobotArmBase):
    """机械臂状态配置创建模式"""
    pass


class RobotArmUpdate(BaseSchema):
    """机械臂状态配置更新模式"""
    robot_arm_ip: Optional[str] = Field(None, description="机械臂IP地址")
    subnet_mask: Optional[str] = Field(None, description="子网掩码")
    gateway: Optional[str] = Field(None, description="网关地址")
    robot_arm_port: Optional[int] = Field(None, ge=1, le=65535, description="机械臂端口号(1-65535)")
    operating_speed: Optional[int] = Field(None, ge=0, le=100, description="机械臂运行速度(0-100%)")
    origin_coordinates: Optional[List[float]] = Field(None, min_items=6, max_items=6, description="机械臂原点坐标(6个数值)")
    plane_coordinates: Optional[List[float]] = Field(None, min_items=6, max_items=6, description="机械臂平面坐标(6个数值)")
    load_size: Optional[Decimal] = Field(None, ge=0.00, le=100.00, description="机械臂负载大小(kg)")
    end_coordinates: Optional[List[float]] = Field(None, min_items=6, max_items=6, description="机械臂末端坐标(6个数值)")
    tool_io: Optional[int] = Field(None, ge=0, le=255, description="机械臂工具IO(0-255)")
    collision_detection_level: Optional[str] = Field(None, description="机械臂碰撞检测级别")
    
    @validator('robot_arm_ip')
    def validate_robot_arm_ip(cls, v):
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
    
    @validator('collision_detection_level')
    def validate_collision_level(cls, v):
        if v is not None and v not in ['低', '中', '高']:
            raise ValueError('碰撞检测级别必须是: 低、中、高')
        return v
    
    @validator('origin_coordinates')
    def validate_origin_coordinates(cls, v):
        if v is not None and len(v) != 6:
            raise ValueError('原点坐标必须包含6个数值')
        return v
    
    @validator('plane_coordinates')
    def validate_plane_coordinates(cls, v):
        if v is not None and len(v) != 6:
            raise ValueError('平面坐标必须包含6个数值')
        return v
    
    @validator('end_coordinates')
    def validate_end_coordinates(cls, v):
        if v is not None and len(v) != 6:
            raise ValueError('末端坐标必须包含6个数值')
        return v


class RobotArmResponse(BaseResponse):
    """机械臂状态配置响应模式"""
    id: str = Field(..., description="机械臂状态配置ID")
    robot_arm_ip: str = Field(..., description="机械臂IP地址")
    subnet_mask: str = Field(..., description="子网掩码")
    gateway: str = Field(..., description="网关地址")
    robot_arm_port: int = Field(..., description="机械臂端口号(1-65535)")
    operating_speed: int = Field(..., description="机械臂运行速度(0-100%)")
    origin_coordinates: List[float] = Field(..., description="机械臂原点坐标(6个数值)")
    plane_coordinates: List[float] = Field(..., description="机械臂平面坐标(6个数值)")
    load_size: Decimal = Field(..., description="机械臂负载大小(kg)")
    end_coordinates: List[float] = Field(..., description="机械臂末端坐标(6个数值)")
    tool_io: int = Field(..., description="机械臂工具IO(0-255)")
    collision_detection_level: str = Field(..., description="机械臂碰撞检测级别")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class RobotArmQuery(BaseSchema):
    """机械臂状态配置查询模式"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(20, ge=1, le=100, description="每页数量")
    robot_arm_ip: Optional[str] = Field(None, description="机械臂IP筛选")
    robot_arm_port: Optional[int] = Field(None, description="机械臂端口筛选")
    operating_speed: Optional[int] = Field(None, description="运行速度筛选")
    collision_detection_level: Optional[str] = Field(None, description="碰撞检测级别筛选")


class RobotArmListResponse(BaseSchema):
    """机械臂状态配置列表响应模式"""
    items: List[RobotArmResponse] = Field(..., description="机械臂状态配置列表")
    total: int = Field(..., description="总数")
