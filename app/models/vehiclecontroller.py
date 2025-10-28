"""
车体控制器数据模型
"""

from sqlalchemy import Column, String, JSON, Boolean, DECIMAL, Integer, Index
from .base import BaseModel


class VehicleController(BaseModel):
    """车体控制器模型"""
    
    __tablename__ = "cfg_vehicle_controller"
    
    # 车体基础参数
    vehicle_model = Column(String(50), nullable=False, comment="车体模型：双轮差速/四轮差速/四驱四转/单舵轮/双舵轮")
    wheel_diameter = Column(DECIMAL(8, 2), nullable=False, comment="车轮直径(mm)")
    reduction_ratio = Column(Integer, nullable=False, comment="车体减速比")
    wheelbase = Column(DECIMAL(8, 2), nullable=False, comment="车体轴距(mm)")
    track_width = Column(DECIMAL(8, 2), nullable=False, comment="车体轮距(mm)")
    max_linear_velocity = Column(DECIMAL(8, 3), nullable=False, comment="车体最大线速度(m/s)")
    max_angular_velocity = Column(DECIMAL(8, 3), nullable=False, comment="车体最大角速度(rad/s)")
    
    # 串口通讯配置（JSON数组，支持4组）
    serial_configs = Column(JSON, nullable=False, comment="串口通讯配置数组")
    
    # 以太网通讯配置（JSON数组，支持2组）
    ethernet_configs = Column(JSON, nullable=False, comment="以太网通讯配置数组")
    
    # 控制器管理
    controller_version = Column(String(20), nullable=False, comment="控制器版本")
    remote_upgrade_enabled = Column(Boolean, nullable=False, default=False, comment="远程升级是否开启")
    
    # 创建索引
    __table_args__ = (
        Index('idx_vehicle_model', 'vehicle_model'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<VehicleController(id='{self.id}', vehicle_model='{self.vehicle_model}')>"

