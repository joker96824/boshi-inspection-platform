"""
深度相机配置数据模型
"""

from sqlalchemy import Column, String, Integer, DECIMAL, Enum, Index, ForeignKey
from sqlalchemy.orm import relationship
from .base import BaseModel


class DepthCamera(BaseModel):
    """深度相机配置模型"""
    
    __tablename__ = "cfg_depth_camera"
    
    # 关联机器人
    robot_id = Column(String(36), ForeignKey("tb_robot.id", ondelete="CASCADE"), nullable=False, index=True, comment="关联机器人ID")
    
    # 深度相机配置参数
    serial_port_id = Column(Integer, nullable=False, default=0, comment="串口ID(0-255)")
    camera_mode = Column(String(50), nullable=True, comment="相机模式")
    image_flip = Column(Enum('上下翻转', '左右翻转', '中心翻转', name='image_flip'), nullable=True, comment="图像翻转")
    image_alignment = Column(String(50), nullable=True, comment="图像对齐")
    
    # 关系
    robot = relationship("Robot", foreign_keys=[robot_id])
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_id', 'robot_id'),
        Index('idx_serial_port_id', 'serial_port_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<DepthCamera(id='{self.id}', serial_port_id={self.serial_port_id}, robot_id='{self.robot_id}')>"

