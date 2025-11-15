"""
机器人数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from .base import BaseModel


class Robot(BaseModel):
    """机器人模型"""
    
    __tablename__ = "tb_robot"
    
    # 基础字段
    robot_name = Column(String(100), nullable=False, comment="机器人名称")
    robot_info = Column(JSON, nullable=True, comment="机器人信息")
    factory_id = Column(String(36), ForeignKey("tb_factory.id", ondelete="SET NULL"), nullable=True, index=True, comment="厂区ID")
    
    # 关系
    factory = relationship("Factory", foreign_keys=[factory_id], back_populates="robots")
    maps = relationship("RobotMap", back_populates="robot", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="robot")
    
    # 创建索引
    __table_args__ = (
        Index('idx_robot_name', 'robot_name'),
        Index('idx_factory_id', 'factory_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_deleted', 'is_deleted'),
    )
    
    def __repr__(self):
        return f"<Robot(id='{self.id}', robot_name='{self.robot_name}')>"
