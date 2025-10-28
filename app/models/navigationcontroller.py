"""
导航控制器配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Index
from .base import BaseModel


class NavigationController(BaseModel):
    """导航控制器配置模型"""
    
    __tablename__ = "cfg_navigation_controller"
    
    # 控制器基本信息
    module_group = Column(Integer, nullable=False, default=1, comment="模块组编号(支持多组配置)")
    
    # 网络配置
    ethernet_ip = Column(String(15), nullable=False, comment="以太网通讯IP地址")
    subnet_mask = Column(String(15), nullable=False, default="255.255.255.0", comment="子网掩码")
    gateway = Column(String(15), nullable=False, default="192.168.1.1", comment="网关地址")
    ethernet_port = Column(Integer, nullable=False, comment="以太网通讯端口号(1-65535)")
    baud_rate = Column(Integer, nullable=False, default=9600, comment="波特率(9600-115200)")
    
    # 导航参数
    deceleration_distance = Column(DECIMAL(8, 2), nullable=False, default=800.00, comment="减速距离(mm)")
    stop_distance = Column(DECIMAL(8, 2), nullable=False, default=1500.00, comment="停止距离(mm)")
    max_linear_velocity = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="路径最大线速度(m/s)")
    max_angular_velocity = Column(DECIMAL(8, 3), nullable=False, default=0.100, comment="路径最大角速度(rad/s)")
    acceleration = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="加速度(m/s²)")
    deceleration = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="减速度(m/s²)")
    expansion_coefficient = Column(DECIMAL(8, 2), nullable=False, default=0.00, comment="膨胀系数(0-2.0)")
    
    # 创建索引
    __table_args__ = (
        Index('idx_module_group', 'module_group'),
        Index('idx_ethernet_ip', 'ethernet_ip'),
        Index('idx_ethernet_port', 'ethernet_port'),
        Index('idx_baud_rate', 'baud_rate'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<NavigationController(id='{self.id}', module_group={self.module_group})>"

