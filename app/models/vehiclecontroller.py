"""
车体控制器数据模型
"""

from sqlalchemy import Column, String, Boolean, DECIMAL, Integer, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class VehicleController(BaseModel):
    """车体控制器模型"""
    
    __tablename__ = "cfg_vehicle_controller"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 车体基础参数
    vehicle_model = Column(String(50), nullable=False, comment="车体模型：双轮差速/四轮差速/四驱四转/单舵轮/双舵轮")
    wheel_diameter = Column(DECIMAL(8, 2), nullable=False, comment="车轮直径(mm)")
    reduction_ratio = Column(Integer, nullable=False, comment="车体减速比")
    wheelbase = Column(DECIMAL(8, 2), nullable=False, comment="车体轴距(mm)")
    track_width = Column(DECIMAL(8, 2), nullable=False, comment="车体轮距(mm)")
    max_linear_velocity = Column(DECIMAL(8, 3), nullable=False, comment="车体最大线速度(m/s)")
    max_angular_velocity = Column(DECIMAL(8, 3), nullable=False, comment="车体最大角速度(rad/s)")
    
    # 串口通讯配置（4组，每组3个参数：站号、波特率、功能码）
    serial_1_station_number = Column(Integer, nullable=True, comment="串口1站号(1-255)")
    serial_1_baud_rate = Column(Integer, nullable=True, comment="串口1波特率(9600-115200)")
    serial_1_function_code = Column(Integer, nullable=True, comment="串口1功能码")
    serial_2_station_number = Column(Integer, nullable=True, comment="串口2站号(1-255)")
    serial_2_baud_rate = Column(Integer, nullable=True, comment="串口2波特率(9600-115200)")
    serial_2_function_code = Column(Integer, nullable=True, comment="串口2功能码")
    serial_3_station_number = Column(Integer, nullable=True, comment="串口3站号(1-255)")
    serial_3_baud_rate = Column(Integer, nullable=True, comment="串口3波特率(9600-115200)")
    serial_3_function_code = Column(Integer, nullable=True, comment="串口3功能码")
    serial_4_station_number = Column(Integer, nullable=True, comment="串口4站号(1-255)")
    serial_4_baud_rate = Column(Integer, nullable=True, comment="串口4波特率(9600-115200)")
    serial_4_function_code = Column(Integer, nullable=True, comment="串口4功能码")
    
    # 以太网通讯配置（用编号区分，每组：IP地址、子网掩码、网关、端口、波特率、通讯模式）
    ethernet_1_ip_address = Column(String(15), nullable=True, comment="以太网1IP地址")
    ethernet_1_subnet_mask = Column(String(15), nullable=True, comment="以太网1子网掩码")
    ethernet_1_gateway = Column(String(15), nullable=True, comment="以太网1网关")
    ethernet_1_port = Column(Integer, nullable=True, comment="以太网1端口(1-65535)")
    ethernet_1_baud_rate = Column(Integer, nullable=True, comment="以太网1波特率(9600-115200)")
    ethernet_1_communication_mode = Column(String(20), nullable=True, comment="以太网1通讯模式：server/client")
    ethernet_2_ip_address = Column(String(15), nullable=True, comment="以太网2IP地址")
    ethernet_2_subnet_mask = Column(String(15), nullable=True, comment="以太网2子网掩码")
    ethernet_2_gateway = Column(String(15), nullable=True, comment="以太网2网关")
    ethernet_2_port = Column(Integer, nullable=True, comment="以太网2端口(1-65535)")
    ethernet_2_baud_rate = Column(Integer, nullable=True, comment="以太网2波特率(9600-115200)")
    ethernet_2_communication_mode = Column(String(20), nullable=True, comment="以太网2通讯模式：server/client")
    
    # 控制器管理
    controller_version = Column(String(20), nullable=False, comment="控制器版本")
    remote_upgrade_enabled = Column(Boolean, nullable=False, default=False, comment="远程升级是否开启")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_vehicle_model', 'vehicle_model'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<VehicleController(id='{self.id}', vehicle_model='{self.vehicle_model}', robot_id='{self.robot_id}')>"

