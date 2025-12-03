"""
导航控制器配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class NavigationController(BaseModel):
    """导航控制器配置模型"""
    
    __tablename__ = "cfg_navigation_controller"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 以太网通讯配置（2组，用编号区分）
    # 以太网1配置
    ethernet_1_ip = Column(String(15), nullable=True, comment="以太网1IP地址")
    ethernet_1_subnet_mask = Column(String(15), nullable=True, comment="以太网1子网掩码")
    ethernet_1_gateway = Column(String(15), nullable=True, comment="以太网1网关")
    ethernet_1_port = Column(Integer, nullable=True, comment="以太网1端口号(1-65535)")
    ethernet_1_baud_rate = Column(Integer, nullable=True, comment="以太网1波特率(9600-115200)")
    
    # 以太网2配置
    ethernet_2_ip = Column(String(15), nullable=True, comment="以太网2IP地址")
    ethernet_2_subnet_mask = Column(String(15), nullable=True, comment="以太网2子网掩码")
    ethernet_2_gateway = Column(String(15), nullable=True, comment="以太网2网关")
    ethernet_2_port = Column(Integer, nullable=True, comment="以太网2端口号(1-65535)")
    ethernet_2_baud_rate = Column(Integer, nullable=True, comment="以太网2波特率(9600-115200)")
    
    # 导航参数
    deceleration_distance = Column(DECIMAL(8, 2), nullable=False, default=800.00, comment="减速距离(mm)")
    stop_distance = Column(DECIMAL(8, 2), nullable=False, default=1500.00, comment="停止距离(mm)")
    max_linear_velocity = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="路径最大线速度(m/s)")
    max_angular_velocity = Column(DECIMAL(8, 3), nullable=False, default=0.100, comment="路径最大角速度(rad/s)")
    acceleration = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="加速度(m/s²)")
    deceleration = Column(DECIMAL(8, 3), nullable=False, default=0.800, comment="减速度(m/s²)")
    expansion_coefficient = Column(DECIMAL(8, 2), nullable=False, default=0.00, comment="膨胀系数(0-2.0)")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_ethernet_1_ip', 'ethernet_1_ip'),
        Index('idx_ethernet_1_port', 'ethernet_1_port'),
        Index('idx_ethernet_2_ip', 'ethernet_2_ip'),
        Index('idx_ethernet_2_port', 'ethernet_2_port'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<NavigationController(id='{self.id}', robot_id='{self.robot_id}')>"

