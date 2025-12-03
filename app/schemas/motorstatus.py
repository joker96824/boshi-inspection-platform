"""
电机状态配置数据验证模式
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from .base import BaseSchema, BaseResponse


class MotorStatusBase(BaseSchema):
    """电机状态配置基础模式"""
    motor_id: int = Field(..., ge=0, le=255, description="电机ID(0-255)")
    baud_rate: int = Field(..., description="波特率(9600-115200)")
    tpdo_config: Optional[Dict[str, Any]] = Field(None, description="TPDO配置参数")
    rpdo_config: Optional[Dict[str, Any]] = Field(None, description="RPDO配置参数")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
        if v not in valid_rates:
            raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v
    
    @validator('tpdo_config')
    def validate_tpdo_config(cls, v):
        if v is not None:
            required_fields = ['enabled', 'transmission_type', 'inhibit_time', 'event_timer', 'sync_start_value']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'TPDO配置缺少必需字段: {field}')
            
            if not isinstance(v['enabled'], bool):
                raise ValueError('enabled字段必须是布尔值')
            
            if v['transmission_type'] not in ['synchronous', 'asynchronous']:
                raise ValueError('transmission_type必须是synchronous或asynchronous')
            
            if not isinstance(v['inhibit_time'], int) or v['inhibit_time'] < 0:
                raise ValueError('inhibit_time必须是非负整数')
            
            if not isinstance(v['event_timer'], int) or v['event_timer'] < 0:
                raise ValueError('event_timer必须是非负整数')
            
            if not isinstance(v['sync_start_value'], int) or v['sync_start_value'] < 0:
                raise ValueError('sync_start_value必须是非负整数')
        return v
    
    @validator('rpdo_config')
    def validate_rpdo_config(cls, v):
        if v is not None:
            required_fields = ['enabled', 'transmission_type', 'inhibit_time', 'event_timer', 'sync_start_value']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'RPDO配置缺少必需字段: {field}')
            
            if not isinstance(v['enabled'], bool):
                raise ValueError('enabled字段必须是布尔值')
            
            if v['transmission_type'] not in ['synchronous', 'asynchronous']:
                raise ValueError('transmission_type必须是synchronous或asynchronous')
            
            if not isinstance(v['inhibit_time'], int) or v['inhibit_time'] < 0:
                raise ValueError('inhibit_time必须是非负整数')
            
            if not isinstance(v['event_timer'], int) or v['event_timer'] < 0:
                raise ValueError('event_timer必须是非负整数')
            
            if not isinstance(v['sync_start_value'], int) or v['sync_start_value'] < 0:
                raise ValueError('sync_start_value必须是非负整数')
        return v


class MotorStatusCreate(MotorStatusBase):
    """电机状态配置创建模式"""
    pass


class MotorStatusUpdate(BaseSchema):
    """电机状态配置更新模式"""
    motor_id: Optional[int] = Field(None, ge=0, le=255, description="电机ID(0-255)")
    baud_rate: Optional[int] = Field(None, description="波特率(9600-115200)")
    tpdo_config: Optional[Dict[str, Any]] = Field(None, description="TPDO配置参数")
    rpdo_config: Optional[Dict[str, Any]] = Field(None, description="RPDO配置参数")
    
    @validator('baud_rate')
    def validate_baud_rate(cls, v):
        if v is not None:
            valid_rates = [9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600]
            if v not in valid_rates:
                raise ValueError(f'波特率必须是以下值之一: {valid_rates}')
        return v
    
    @validator('tpdo_config')
    def validate_tpdo_config(cls, v):
        if v is not None:
            required_fields = ['enabled', 'transmission_type', 'inhibit_time', 'event_timer', 'sync_start_value']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'TPDO配置缺少必需字段: {field}')
            
            if not isinstance(v['enabled'], bool):
                raise ValueError('enabled字段必须是布尔值')
            
            if v['transmission_type'] not in ['synchronous', 'asynchronous']:
                raise ValueError('transmission_type必须是synchronous或asynchronous')
            
            if not isinstance(v['inhibit_time'], int) or v['inhibit_time'] < 0:
                raise ValueError('inhibit_time必须是非负整数')
            
            if not isinstance(v['event_timer'], int) or v['event_timer'] < 0:
                raise ValueError('event_timer必须是非负整数')
            
            if not isinstance(v['sync_start_value'], int) or v['sync_start_value'] < 0:
                raise ValueError('sync_start_value必须是非负整数')
        return v
    
    @validator('rpdo_config')
    def validate_rpdo_config(cls, v):
        if v is not None:
            required_fields = ['enabled', 'transmission_type', 'inhibit_time', 'event_timer', 'sync_start_value']
            for field in required_fields:
                if field not in v:
                    raise ValueError(f'RPDO配置缺少必需字段: {field}')
            
            if not isinstance(v['enabled'], bool):
                raise ValueError('enabled字段必须是布尔值')
            
            if v['transmission_type'] not in ['synchronous', 'asynchronous']:
                raise ValueError('transmission_type必须是synchronous或asynchronous')
            
            if not isinstance(v['inhibit_time'], int) or v['inhibit_time'] < 0:
                raise ValueError('inhibit_time必须是非负整数')
            
            if not isinstance(v['event_timer'], int) or v['event_timer'] < 0:
                raise ValueError('event_timer必须是非负整数')
            
            if not isinstance(v['sync_start_value'], int) or v['sync_start_value'] < 0:
                raise ValueError('sync_start_value必须是非负整数')
        return v


class MotorStatusResponse(BaseResponse):
    """电机状态配置响应模式"""
    id: str = Field(..., description="电机状态配置ID")
    motor_id: int = Field(..., description="电机ID(0-255)")
    baud_rate: int = Field(..., description="波特率(9600-115200)")
    tpdo_config: Optional[Dict[str, Any]] = Field(None, description="TPDO配置参数")
    rpdo_config: Optional[Dict[str, Any]] = Field(None, description="RPDO配置参数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
    created_by: Optional[str] = Field(None, description="创建者")
    updated_by: Optional[str] = Field(None, description="更新者")


class MotorStatusQuery(BaseSchema):
    """电机状态配置查询模式"""
    page: Optional[int] = Field(None, gt=0, description="页码（可选，大于0，必须与size同时提供）")
    size: Optional[int] = Field(None, gt=0, description="每页数量（可选，大于0，必须与page同时提供）")
    motor_id: Optional[int] = Field(None, description="电机ID筛选")
    baud_rate: Optional[int] = Field(None, description="波特率筛选")


class MotorStatusListResponse(BaseSchema):
    """电机状态配置列表响应模式"""
    items: List[MotorStatusResponse] = Field(..., description="电机状态配置列表")
    total: int = Field(..., description="总数")


class MotorStatusBatchUpdate(BaseSchema):
    """电机状态配置批量更新模式（按机器人）"""
    robot_id: str = Field(..., description="机器人ID")
    configs: List[MotorStatusCreate] = Field(..., description="电机状态配置列表")