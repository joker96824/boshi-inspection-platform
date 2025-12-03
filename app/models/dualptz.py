"""
双光云台配置数据模型
"""

from sqlalchemy import Column, String, Integer, Boolean, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class DualPTZ(BaseModel):
    """双光云台配置模型"""
    
    __tablename__ = "cfg_dual_ptz"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 网络配置
    ptz_ip = Column(String(15), nullable=False, comment="云台IP地址")
    subnet_mask = Column(String(15), nullable=False, default="255.255.255.0", comment="子网掩码")
    gateway = Column(String(15), nullable=False, default="192.168.1.1", comment="网关地址")
    
    # 运行参数
    operating_speed = Column(Integer, nullable=False, default=100, comment="运行速度(1-255)")
    fill_light_enabled = Column(Boolean, nullable=False, default=False, comment="补光灯开启状态")
    wiper_enabled = Column(Boolean, nullable=False, default=False, comment="雨刷开启状态")
    auto_focus_enabled = Column(Boolean, nullable=False, default=True, comment="自动对焦开启状态")
    backlight_compensation_enabled = Column(Boolean, nullable=False, default=False, comment="逆光补偿开启状态")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_ptz_ip', 'ptz_ip'),
        Index('idx_operating_speed', 'operating_speed'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<DualPTZ(id='{self.id}', ptz_ip='{self.ptz_ip}', operating_speed={self.operating_speed}, robot_id='{self.robot_id}')>"

