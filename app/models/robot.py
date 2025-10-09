"""
机器人数据模型
"""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseModel


class Robot(BaseModel):
    """机器人模型"""
    
    __tablename__ = "tb_robot"
    
    # 基础字段
    user_id = Column(String(36), ForeignKey("tb_users.id", ondelete="CASCADE"), nullable=False, comment="所属用户ID")
    robot_name = Column(String(100), nullable=False, comment="机器人名称")
    robot_info = Column(JSON, nullable=True, comment="机器人信息")
    
    # 关系
    user = relationship("User", back_populates="robots")
    tasks = relationship("Task", back_populates="robot")
    
    def __repr__(self):
        return f"<Robot(id='{self.id}', robot_name='{self.robot_name}', user_id='{self.user_id}')>"
