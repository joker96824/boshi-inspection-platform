"""
车体控制器数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class SerialConfig(BaseModel):
    """串口配置模式"""
    module_index: int = Field(..., ge=1, le=4, description="模块索引(1-4)")
    station_number: int = Field(..., ge=0, le=255, description="串口通讯站号")
    baud_rate: int = Field(..., description="串口通讯波特率")
    function_code: int = Field(..., ge=1, le=10, description="串口通讯功能")
    enabled: bool = Field(True, description="是否启用")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if v not in valid_rates:
            raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v


class EthernetConfig(BaseModel):
    """以太网配置模式"""
    module_index: int = Field(..., ge=1, le=2, description="模块索引(1-2)")
    ip_address: str = Field(..., description="IP地址")
    subnet_mask: str = Field(..., description="子网掩码")
    gateway: str = Field(..., description="网关")
    port: int = Field(..., ge=1, le=65535, description="端口")
    baud_rate: int = Field(..., ge=9600, le=115200, description="波特率")
    communication_mode: str = Field(..., description="通讯模式：server/client")
    enabled: bool = Field(True, description="是否启用")
    
    @validator('communication_mode')
    def validate_communication_mode(cls, v):
        if v not in ['server', 'client']:
            raise ValueError('通讯模式必须是 server 或 client')
        return v


class VehicleControllerBase(BaseSchema):
    """车体控制器基础模式"""
    vehicle_model: str = Field(..., description="车体模型")
    wheel_diameter: float = Field(..., gt=0, description="车轮直径(mm)")
    reduction_ratio: int = Field(..., gt=0, description="车体减速比")
    wheelbase: float = Field(..., gt=0, description="车体轴距(mm)")
    track_width: float = Field(..., gt=0, description="车体轮距(mm)")
    max_linear_velocity: float = Field(..., gt=0, description="车体最大线速度(m/s)")
    max_angular_velocity: float = Field(..., gt=0, description="车体最大角速度(rad/s)")
    serial_configs: List[SerialConfig] = Field(..., max_length=4, description="串口通讯配置")
    ethernet_configs: List[EthernetConfig] = Field(..., max_length=2, description="以太网通讯配置")
    controller_version: str = Field(..., description="控制器版本")
    remote_upgrade_enabled: bool = Field(False, description="远程升级是否开启")
    
    @validator('vehicle_model')
    def validate_vehicle_model(cls, v):
        valid_models = ['双轮差速', '四轮差速', '四驱四转', '单舵轮', '双舵轮']
        if v not in valid_models:
            raise ValueError(f'车体模型必须是以下值之一: {valid_models}')
        return v
    
    @validator('serial_configs')
    def validate_serial_configs(cls, v):
        if len(v) > 4:
            raise ValueError('串口配置最多支持4组')
        # 检查module_index是否重复
        indices = [config.module_index for config in v]
        if len(indices) != len(set(indices)):
            raise ValueError('串口配置的module_index不能重复')
        return v
    
    @validator('ethernet_configs')
    def validate_ethernet_configs(cls, v):
        if len(v) > 2:
            raise ValueError('以太网配置最多支持2组')
        # 检查module_index是否重复
        indices = [config.module_index for config in v]
        if len(indices) != len(set(indices)):
            raise ValueError('以太网配置的module_index不能重复')
        return v


class VehicleControllerCreate(VehicleControllerBase):
    """车体控制器创建模式"""
    pass


class VehicleControllerUpdate(BaseSchema):
    """车体控制器更新模式"""
    vehicle_model: Optional[str] = Field(None, description="车体模型")
    wheel_diameter: Optional[float] = Field(None, gt=0, description="车轮直径(mm)")
    reduction_ratio: Optional[int] = Field(None, gt=0, description="车体减速比")
    wheelbase: Optional[float] = Field(None, gt=0, description="车体轴距(mm)")
    track_width: Optional[float] = Field(None, gt=0, description="车体轮距(mm)")
    max_linear_velocity: Optional[float] = Field(None, gt=0, description="车体最大线速度(m/s)")
    max_angular_velocity: Optional[float] = Field(None, gt=0, description="车体最大角速度(rad/s)")
    
    # 串口配置（扁平格式，与数据库字段对应）
    serial_1_station_number: Optional[int] = Field(None, ge=0, le=255, description="串口1站号(0-255)")
    serial_1_baud_rate: Optional[int] = Field(None, description="串口1波特率")
    serial_1_function_code: Optional[int] = Field(None, ge=1, le=10, description="串口1功能码")
    serial_2_station_number: Optional[int] = Field(None, ge=0, le=255, description="串口2站号(0-255)")
    serial_2_baud_rate: Optional[int] = Field(None, description="串口2波特率")
    serial_2_function_code: Optional[int] = Field(None, ge=1, le=10, description="串口2功能码")
    serial_3_station_number: Optional[int] = Field(None, ge=0, le=255, description="串口3站号(0-255)")
    serial_3_baud_rate: Optional[int] = Field(None, description="串口3波特率")
    serial_3_function_code: Optional[int] = Field(None, ge=1, le=10, description="串口3功能码")
    serial_4_station_number: Optional[int] = Field(None, ge=0, le=255, description="串口4站号(0-255)")
    serial_4_baud_rate: Optional[int] = Field(None, description="串口4波特率")
    serial_4_function_code: Optional[int] = Field(None, ge=1, le=10, description="串口4功能码")
    
    # 以太网配置（扁平格式，与数据库字段对应）
    ethernet_1_ip_address: Optional[str] = Field(None, description="以太网1IP地址")
    ethernet_1_subnet_mask: Optional[str] = Field(None, description="以太网1子网掩码")
    ethernet_1_gateway: Optional[str] = Field(None, description="以太网1网关")
    ethernet_1_port: Optional[int] = Field(None, ge=1, le=65535, description="以太网1端口")
    ethernet_1_baud_rate: Optional[int] = Field(None, ge=9600, le=115200, description="以太网1波特率")
    ethernet_1_communication_mode: Optional[str] = Field(None, description="以太网1通讯模式：server/client")
    ethernet_2_ip_address: Optional[str] = Field(None, description="以太网2IP地址")
    ethernet_2_subnet_mask: Optional[str] = Field(None, description="以太网2子网掩码")
    ethernet_2_gateway: Optional[str] = Field(None, description="以太网2网关")
    ethernet_2_port: Optional[int] = Field(None, ge=1, le=65535, description="以太网2端口")
    ethernet_2_baud_rate: Optional[int] = Field(None, ge=9600, le=115200, description="以太网2波特率")
    ethernet_2_communication_mode: Optional[str] = Field(None, description="以太网2通讯模式：server/client")
    
    controller_version: Optional[str] = Field(None, description="控制器版本")
    remote_upgrade_enabled: Optional[bool] = Field(None, description="远程升级是否开启")
    
    @validator('serial_1_baud_rate', 'serial_2_baud_rate', 'serial_3_baud_rate', 'serial_4_baud_rate')
    def validate_serial_baud_rate(cls, v):
        if v is not None:
            valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
            if v not in valid_rates:
                raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v
    
    @validator('ethernet_1_communication_mode', 'ethernet_2_communication_mode')
    def validate_communication_mode(cls, v):
        if v is not None:
            if v not in ['server', 'client']:
                raise ValueError('通讯模式必须是 server 或 client')
        return v


class VehicleControllerResponse(BaseResponse):
    """车体控制器响应模式"""
    id: str = Field(..., description="车体控制器ID")
    vehicle_model: str = Field(..., description="车体模型")
    wheel_diameter: float = Field(..., description="车轮直径(mm)")
    reduction_ratio: int = Field(..., description="车体减速比")
    wheelbase: float = Field(..., description="车体轴距(mm)")
    track_width: float = Field(..., description="车体轮距(mm)")
    max_linear_velocity: float = Field(..., description="车体最大线速度(m/s)")
    max_angular_velocity: float = Field(..., description="车体最大角速度(rad/s)")
    serial_configs: List[Dict[str, Any]] = Field(..., description="串口通讯配置")
    ethernet_configs: List[Dict[str, Any]] = Field(..., description="以太网通讯配置")
    controller_version: str = Field(..., description="控制器版本")
    remote_upgrade_enabled: bool = Field(..., description="远程升级是否开启")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class VehicleControllerQuery(BaseSchema):
    """车体控制器查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    vehicle_model: Optional[str] = Field(None, description="车体模型筛选")


class VehicleControllerListResponse(BaseSchema):
    """车体控制器列表响应模式"""
    items: List[VehicleControllerResponse] = Field(..., description="车体控制器列表")
    total: int = Field(..., description="总数")
