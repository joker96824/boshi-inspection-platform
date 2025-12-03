"""
机械臂状态配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, JSON, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class RobotArm(BaseModel):
    """机械臂状态配置模型"""
    
    __tablename__ = "cfg_robot_arm"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 网络配置
    robot_arm_ip = Column(String(15), nullable=False, comment="机械臂IP地址")
    subnet_mask = Column(String(15), nullable=False, default="255.255.255.0", comment="子网掩码")
    gateway = Column(String(15), nullable=False, default="192.168.1.1", comment="网关地址")
    robot_arm_port = Column(Integer, nullable=False, comment="机械臂端口号(1-65535)")
    
    # 机械臂参数
    operating_speed = Column(Integer, nullable=False, default=50, comment="机械臂运行速度(0-100%)")
    origin_coordinates = Column(JSON, nullable=False, comment="机械臂原点坐标")
    plane_coordinates = Column(JSON, nullable=False, comment="机械臂平面坐标")
    load_size = Column(DECIMAL(5, 2), nullable=False, default=0.50, comment="机械臂负载大小(kg)")
    end_coordinates = Column(JSON, nullable=False, comment="机械臂末端坐标")
    tool_io = Column(Integer, nullable=False, default=0, comment="机械臂工具IO(0-255)")
    collision_detection_level = Column(Enum('低', '中', '高', name='collision_level'), nullable=False, default='中', comment="机械臂碰撞检测级别")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_robot_arm_ip', 'robot_arm_ip'),
        Index('idx_robot_arm_port', 'robot_arm_port'),
        Index('idx_operating_speed', 'operating_speed'),
        Index('idx_collision_level', 'collision_detection_level'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<RobotArm(id='{self.id}', robot_arm_ip='{self.robot_arm_ip}', port={self.robot_arm_port}, robot_id='{self.robot_id}')>"

